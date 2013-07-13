
def tweetUnescape(text):
	"""
		there are three special characters
		  that would be escaped when returned by twitter API:
		  * "<" => "&lt;"
		  ; ">" => "&gt;"
		  ; "&" => "&amp;"

		I've done a lot of searching to find some official document
		  describing these kinds of behavior but with no luck.

		So these function is regarded as a hacking method

		When the escaping behavior is officially confirmed,
		  this method should be moved out of this file.

	"""
	return text \
		.replace("&lt;", "<") \
		.replace("&gt;", ">") \
		.replace("&amp;", "&")
