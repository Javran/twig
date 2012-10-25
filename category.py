from command import lookForCommand
import re

# add number in the value thus we can arrange category by simply sorting
category_description = {
	"help":		(0, "Help document or helpful tools"),
	"account": 	(1, "Account management"),
	"ttweet":	(2, "Tweet or timeline"),
	"tfriend":	(3, "Friendship or user information"),
	"tlist":	(4, "List"),
	"tfav":		(5, "Favorites"),
	"tdm":		(6, "Direct message"),
	"other":	(7, "Other command"),
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
	
	return (category, category_description[category][1])
