import pycurl, json, re, datetime
from operator import itemgetter

print "Welcome to Twitalectology!"
print "Developed by Brice Russ, rbruss@gmail.com"
print "Pick a number from the following options:"
print "1) Create corpus from Twitter variables"
print "2) Collocate a term in your corpus"
print "3) Process your corpus"
value = raw_input()

def corpbuild():
    STREAM_URL = "http://stream.twitter.com/1/statuses/filter.json"
    
    keywords = raw_input("Type the variants that you wish to track, separated by commas (but not spaces): \n")
    keywords = "track=" + keywords
    
    USER = raw_input("Type your Twitter account username: ")
    PASS = raw_input("Type your Twitter account password: ")
    
    fname = raw_input("Type the name of your output file (including '.txt' extension): ")
 
    boundingbox = [25,-125,49,-66]
    print "Program is running..."
    
    class Client:
      def __init__(self):
        self.buffer = ""
        self.conn = pycurl.Curl()
        self.conn.setopt(pycurl.USERPWD, "%s:%s" % (USER, PASS))
        self.conn.setopt(pycurl.POSTFIELDS, keywords)
        self.conn.setopt(pycurl.POST, 1)
        self.conn.setopt(pycurl.URL, STREAM_URL)
        self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)
        self.conn.perform()   
      def on_receive(self, data):
        output = open('longlat'+fname, 'a')
        self.buffer += data
        if data.endswith("\r\n") and self.buffer.strip():
          try:
            content = json.loads(self.buffer)
            self.buffer = ""
      #      print content
            if "text" in content:
              location = (u"{0[user][location]}".format(content))
              locsearch = re.compile("[0-9]{1,8}[.]{1}[0-9]{1,8}[,][-]?[0-9]{1,8}[.]{1}[0-9]{1,8}")
              latlong = locsearch.search(location)
              if latlong:
                location = latlong.group()
                splitloc = location.split(",")
                if len(splitloc) > 1 and (boundingbox[0] < float(splitloc[0]) < boundingbox[2]) and (boundingbox[1] < float(splitloc[1]) < boundingbox[3]):
                  tweet = u"{0[text]}".format(content)
                  if "RT" not in tweet:
                    try:
                      output.write(location +  '\t' +  tweet.encode("utf-8") + "\n")
                    except (UnicodeEncodeError, UnicodeDecodeError, ValueError):
                        #bad Brice
                        pass;
              else:
                statesearch = re.compile("^[A-Za-z]* *[A-Za-z]* *, *[A-Za-z]{2}$")
                state = statesearch.search(location)
                if state:
                  output2 = open(fname, 'a')
                  location = location.split(',')[0].strip() + ', ' + location.split(',')[1].strip()
                  #print location
                  tweet = u"{0[text]}".format(content)
                  if "RT" not in tweet:
                    try:
                      output2.write(location +  '\t' +  tweet.encode("utf-8") + "\n")
                    except (UnicodeDecodeError, ValueError):
                      pass;
                  output2.close()
                #else:
                #  print "DOES NOT MATCH:", location
          except(ValueError):
            Client()
        output.close()
    client = Client()
    
def collocator():
    input = raw_input("Name of input file? \n")
    input2 = raw_input("Name of word? \n")
    input3 = raw_input("Collocation length? \n")
    input4 = raw_input("(l)eft, (r)ight, or (b)oth collocates? \n")
    input5 = raw_input("Display how many collocates? \n")
    
    item = str(input2)
    cl = int(input3)
    type = str(input4)
    
    def clean(input):
        input = input.strip('\n').strip('\t').strip().strip(',.!?"')
        return input
    
    colDict = {}
    
    for line in open(input):
        line = line.split(" ")
        for i in range(len(line)):
            line[i] = clean(line[i])
            if line[i] == item and len(line) > cl:
                if i > (1 - cl) and (type == "l" or type == "b"):
                    lcol = str(line[i])
                    for j in range(cl):
                        lcol = str(clean(line[i-(j+1)]) + " " + lcol)
                    if lcol not in colDict:
                        colDict[lcol] = 1
                    else:
                        colDict[lcol] += 1
                if (len(line) - cl) > i and (type == "r" or type == "b"):
                    rcol = str(line[i])
                    for j in range(cl):
                        rcol = str(rcol + " " + clean(line[i+(j+1)]))
                    if rcol not in colDict:
                        colDict[rcol] = 1
                    else:
                        colDict[rcol] += 1
                    
    colDict = sorted(colDict.iteritems(), key=itemgetter(1), reverse=True)
    
    topDict = colDict[:(int(input5))]
    
    for item in topDict:
        print item[0], '\t', item[1]
        
def processor():
    input2 = raw_input("Name of state input file? \n")
    
    variables = raw_input("Input your variables, separating groups with semicolons: \n")
    
    def fword(target, line):
        if any([str(" "+target+" ") in line,str(" "+target+"?") in line,str(" "+target+".") in line,str(" "+target+"!") in line,str(" "+target+",") in line,str(" "+target+";") in line,str(" "+target+":") in line,str(" "+target+"\n") in line]):
        #if str(" "+target+("." or " ") in line:
            return True
        else:
            return False
    
    def breakup(variables):
        subg = []
        for group in variables:
            group = group.split(',')
            #print group
            for i, word in enumerate(group):
                group[i] = word.strip()
            subg.append(group)
        return subg
    
    variables = variables.split(';')
    variables = breakup(variables)
        
    v2 = [item for sublist in variables for item in sublist]
            
    if input2:
        temp = open('filteredcity.txt', 'w')
        file2 = open(input2)
        for tweet in file2:
            for item in v2:
                if fword(item,tweet):
                    temp.write(tweet)
        temp.close()
        input2 = "filteredcity.txt"
        file2 = open(input2)
                  
    tweets = []
               
    for tweet in file2:
        line = tweet.split('\t')
        #and likewise down here
        if len(line) > 1:
            location = line[0]
            theTweet = line[1]
            #DON'T FORGET TO RECOMMENT THIS
            city = location.split(',')[0].strip()
            try:
                state = location.split(',')[1].strip()
                tweets.append([city + " " + state, theTweet])
            except IndexError:
                print line
            #tweets.append([location, theTweet])
            #tweets.append([city + ", " + state, theTweet])

    header = "city" + '\t'
    for group in variables:
         header = header + group[0] + '\t'    
    resultsDict = {}
     
    for message in tweets:
        start = []
        for i in range(len(variables)):
            start.append(0)
        if message[0].lower() not in resultsDict:
            #print message[1]
            resultsDict[message[0].lower()] = start
        for a, group in enumerate(variables):
            for unit in group:
                if unit.lower() in message[1].lower():
                    #print resultsDict[message[0].lower()]
                    resultsDict[message[0].lower()][a] += 1
                     
    print header
    
    def tabulate(dictionary, key):
        data = ""
        for a in range(len(variables)):
            data += (str(dictionary[key][a]) + '\t')
        return data
    
    table = open(raw_input("File name of raw table? \n"), 'w')
    table.write(header + "\n")
    for item in resultsDict:
        table.write(item + "\t" + tabulate(resultsDict, item) + "\n")
        
    start = []
    for i in range(len(variables)):
        start.append(0)
    for item in resultsDict:
        for a, unit in enumerate(resultsDict[item]):
            start[a] = start[a] + unit
            
    print start 
    
    def maxnum(list):
        #print list
        high = [0,0]
        for a, number in enumerate(list):
            if number > high[0]:
                high = [number,a]
        return (high[1])           
        
    tabulate = raw_input("Convert data for Google Tables? (y/n) \n")
    if tabulate == 'y':
        output = raw_input("Output file name? (Include .csv extension.) \n")
        outputf = open(output, 'w')
        outputf.write("\t" + "city,value,total \n")
        for item in resultsDict:
            total = 0.0
            for count in resultsDict[item]:
                total = total + count
            if total > 0:
                value = ((resultsDict[item][maxnum(resultsDict[item])])/total) + maxnum(resultsDict[item])
                outputf.write(item + "," + str(value) + "," + str(total) + '\n')        

    
if value == "1":
    corpbuild()
if value == "2":
    collocator()
if value == "3":
    processor()