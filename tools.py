import re
import codecs
import markdown
import urllib

def loadHead(response):
	"""
		load the head part and write it to output 
	"""
	f = open( "./page_src/head.html", "r" )
	html = f.read()
	f.close()
	response.write(html)

def parseMarkdown(src_name, replace_table={}):
	"""
		load markdown source file, do some replacements 
		and parse it to html code

		src_name:	markdown source file name
		replace_table:	dict, key is origin text, and value is the replacement
		
		e.g.: 
		  parseMarkdown( "src.md", { 
		  	"{{phone}}"   : "1234", 
			"{{address}}" : "(N/A)"})
	"""

	# load src markdown file
	src = codecs.open(src_name, "r", encoding="utf-8")
	raw_text = src.read()
	src.close()

	# replace
	for (k, v) in replace_table.iteritems():
		raw_text = raw_text.replace(k, v)

	html = markdown.markdown(raw_text)
	return html

def translate(word, table):
	if table.has_key(word):
		return table[word]
	else:
		return word

def urlesc(txt):
	return urllib.quote( txt.encode('utf-8'), '~')

def parseWhere(raw_where):
	"""
		parse raw where string into arguments
		'raw where' here means strings of which lead with '<' or '>'
		and other part of which is nothing but a number
		for how to use 'where', please refer to command ".where"
		
		'<' is used for time of past   => max_id (inclusive)
		'>' is used for time of future => since_id (exclusive)
	"""
	if len(raw_where) == 0:
		return {}
	
	if raw_where[0] == '<' and raw_where[1:].isdigit():
		# because max_id is inclusive, let's make it exclusive as since_id
		max_id = int ( raw_where[1:] )
		return { "max_id": max_id - 1 }
	if raw_where[0] == '>' and raw_where[1:].isdigit():
		since_id = int ( raw_where[1:] )
		return { "since_id": since_id }
	# error
	return None

def urlMix(url, query_str):
	"""
		mix url with queries
	"""
	if len(query_str) == 0:
		return url
	else:
		return "%s?%s" % (url, query_str)

def mkURL(url, **pairs):
	"""
		combine url with value pairs as queries
		url: origin url without any query or a tail '?'
		pairs: key-value pair
		* keys and values SHOULD NOT be percent-encodes
		  as I will take care of them
	"""
	if len( pairs ) == 0:
		return url
	encoded_params = []
	for k, v in pairs.iteritems():
		ek, ev = urlesc(unicode(k)), urlesc(unicode(v))
		encoded_params.append( "%s=%s" % (ek, ev) )
	
	return urlMix(url, '&'.join( encoded_params ))
