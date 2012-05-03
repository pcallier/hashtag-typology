"""
	twitter_json_to_tsv.py: Convert Twitter JSON output to CSV format for hashtag project
	
	This script is for taking the output from a call to
	Twitter's Streaming API and converting it to
	TSV format, keeping only certain fields.
  For python 2.7.x >_<
"""

import json, logging, re, codecs
from optparse import OptionParser

logging.basicConfig(stream=codecs.open("errors.log",mode="w",encoding="utf8"),level=logging.DEBUG)

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename", help="JSON input file",metavar="FILE")
parser.add_option("-O", "--output", dest="output", help="TSV file for output",metavar="FILE")

(options, args) = parser.parse_args()

logging.debug(options)

clean_tweet_re = re.compile("""[\n\t]""")

input_file = codecs.open(options.filename, mode="r",encoding="utf8")
output_file = codecs.open(options.output, mode="w",encoding="utf8")

# process each line in the input,
# producing appropriate output in the 
# CSV file if possible

# make a header
output_file.write("tweet_id\ttext\tuser_id\tfriends_count\tscreen_name\tuser_name\tcoordinates\tcoordinates_type\tplace_full_name\tplace_country\n")

# TODO fix UNICODE crap again! 
for tweet in input_file:
	tweet_attributes = json.loads(tweet)
	output_file.write(str(tweet_attributes["id"]) + "\t")
	output_file.write(clean_tweet_re.sub("", tweet_attributes["text"]) + "\t")
	output_file.write(str(tweet_attributes["user"]["id_str"]) + "\t")
	output_file.write(str(tweet_attributes["user"]["friends_count"]) + "\t")
	output_file.write(tweet_attributes["user"]["screen_name"] + "\t")
	output_file.write(clean_tweet_re.sub("", tweet_attributes["user"]["name"]) + "\t")
	if tweet_attributes["coordinates"] != None:
		output_file.write(str(tweet_attributes["coordinates"]["coordinates"]) + "\t")
		output_file.write(tweet_attributes["coordinates"]["type"] + "\t")
	else:
		output_file.write("No coords\t\t")
	if tweet_attributes["place"] != None:
		output_file.write(tweet_attributes["place"]["full_name"] + "\t")
		output_file.write(tweet_attributes["place"]["country"] + "\n")
	else:
		output_file.write("No place data\t\t\n")
