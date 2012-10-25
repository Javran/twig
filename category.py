from command import lookForCommand
import re

category_description = {
	"account": 	"Account management",
	"help":		"Help document or helpful tools",
	"ttweet":	"Tweets",
	"tfriend":	"Friendship or user information",
	"tdm":		"Direct messages",
	"tlist":	"Lists",
	"other":	"Other commands"
}
	
def getCategory(cmd):
	"""
		get category of a specific command,
		return (raw_category_word, description) on success
		return (None, None) on failure
	"""
	f = lookForCommand(cmd)
	if f is None:
		return (None, None)

	try:
		category = re.findall( r"# (\S+)", f.__doc__ )[0]
	except:
		category = "other"
	
	return (category, category_description[category])
