import re
import inspect
import twig_command
import twitter_command
from tools import translate

# define a PREFIX for commands
# to send a tweet leading with PREFIX
# duplicate the PREFIX without spaces
# e.g:
#  PREFIX = '.'
#  commands will look like '.xxxxxx'
#  but '..hello' sends a tweet '.hello'
PREFIX = '.'

# for all commands, the format is 
# <PREFIX> <command> <space> [parameters]
# and the parameters would be optional for some commands
# examples for valid command:
#  ".tl twitter"
#                => '.' 'tl' 'twitter'
#  ".dm myfriend a message"
#                => '.' 'dm' 'a message'
#  ".st"
#                => '.' 'st' 

def parseText(text):
	"""
		try to parse text
		* text are 'rstrip'-ed first
		* text leading with two PREFIXs is regarded
		  as messages leading with single PREFIX
		  => return (False, parsed_text)

		* text leading with a PREFIX are all regarded as commands,
		  invalid command will always be parsed as:
		  => return (True, ('', ''))
		  and any valid command products:
		  => return (True, (cmd, raw_params))

		* other text are all parsed as text isself
		  => return (False, parsed_text)
	"""
	text = text.rstrip()
	if text[:2] == PREFIX * 2:
		return (False, text[1:])
	if len(text)>=1 and text[0] == PREFIX:
		newtext = text[1:]
		pattern = re.compile(r'^(\S+)(?:(?:\s+)(.*))?$', re.DOTALL)
		m = pattern.match(newtext)
		if m:
			cmd, params = m.group(1), m.group(2)
			if params is None:
				params = ''
			return (True, (cmd, params))

		# must prevent commands that mismatched with any form below
		# be parsed as text
		return (True, ('', ''))
	
	return (False, text)

# sys commands first, and then twitter api calls
# order:
# 	1. module twig_command
#	2. a instance of twitter_command => create context required by twitter api calls

def lookForCommand(cmd):
	# before looking up, translate cmd if I can recognize what it is
	cmd = translate( cmd, twig_command.alias_table)
	cmd = translate( cmd, twitter_command.alias_table)
	
	# first we do some introspect to find methods in module twig_command
	# a valid function should have a leading 'cmd'
	valid_function = lambda f: \
				inspect.isfunction(f) and \
				f.__name__[:3] == 'cmd' and \
				f.__name__[3:] != ''
	func_list = inspect.getmembers( twig_command, valid_function )

	# check first if we have the required method
	# commands are not case sensive
	for func_name, func in func_list:
		if func_name[3:].lower() == cmd.lower():
			return func

	# a valid method should begin with 'twiCmd'
	valid_method = lambda m: \
				inspect.ismethod(m) and \
				m.__name__[:6] == 'twiCmd' and \
				m.__name__[6:] != ''
	meth_list = inspect.getmembers( twitter_command.TwitterAPIWrapper, valid_method )

	# check if required method is inside TwitterAPIWrapper
	# commands are not case sensive
	for meth_name, meth in meth_list:
		if meth_name[6:].lower() == cmd.lower():
			return meth
	return None

def dispatchCommand(account, cmd, params, r):
	callback = lookForCommand( cmd ) 
	
	if callback is None:
		r.l("!unknown command")
		return
	
	arg1 = inspect.getargspec(callback)[0][0]
	
	if arg1 != 'self':
		# static functions that has 3 arguments
		callback( account, params, r)
		return
	else:
		# let's bring TwitterAPIWrapper into being, 
		# which will provide context for accounts
		try:
			twitter = twitter_command.TwitterAPIWrapper( account )
		except:
			r.l("!unknown account")
			return

		callback( twitter, params, r)
		return

