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
		  as message leading with single PREFIX
		  => return (False, parsed_text)
		* text leading with single PREFIX following a printable char(except spaces)
		  is regarded as command that suits format: .cmd [raw_params]
		  => return (True, (cmd, raw_params)) # raw_params might be ''
		* text that is '' or contains nothing but unprintable chars 
		  are regarded as invalid text
		  => return (False, '')
		* text that cannot suit into rules above are all regarded as text itself
		  => return (False, parsed_text)
	"""
	text = text.rstrip()
	if text[:2] == PREFIX * 2:
		return (False, text[1:])
	if len(text)>1 and text[0] == PREFIX:
		newtext = text[1:]
		# pattern #1: without params
		pat1 = re.compile(r'^(\S+)$')
		m = pat1.match(newtext)
		if m:
			return (True, (m.group(1), ''))
		# pattern #2: with params
		pat2 = re.compile(r'^(\S+)(?:\s+)(.+)$')
		m = pat2.match(newtext)
		if m:
			return (True, (m.group(1), m.group(2)))
		
		# must prevent commands that mismatched with any form below
		# be parsed as text
		return (True, ('', ''))
			
	if len(text) == 0 or text.isspace():
		return (False, '')
	
	return (False, text)

def cmdNotFound(account, params, r):
	r.l( "!unknown command" )

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
		cmdNotFound(account, params, r)
		return
	
	arg1 = inspect.getargspec(callback)[0][0]
	
	if arg1 != 'self':
		# static functions that has 3 arguments
		callback( account, params, r)
		return
	else:
		# let's bring TwitterAPIWrapper into being, 
		# which will provide context for accounts
		twitter = twitter_command.TwitterAPIWrapper( account )
		callback( twitter, params, r)
		return

