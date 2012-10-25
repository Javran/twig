# -*- coding: utf-8 -*-
from google.appengine.ext import db
import twig_db
import re
from twig_db import User, Account, RelationAccountUser
import httplib
import urlparse
import tools
import urllib2
import json

# twig_command module contains cmds that does not require twitter account context
alias_table = {
	"sw" :		"switch",
	"bd" :		"bind",
	"usr":		"user",
	"rmuser":	"unbind",
	"?":		"help",
	"h":		"help",
	"hlp":		"help",
	"lck":		"lengthcheck",
	"len":		"lengthcheck",
	"lscmd":	"commandlist",
	"cmds":		"commandlist",
	"unshort":	"unshortlink",
	"us":		"unshortlink",
}

def cmdBind(account, params, r):
	"""
		# account
		% bind with code       
		% format: .bind <code>  

		* sets active_id as well
	"""
	if len( params ) == 0:
		r.l("!bad argument")
		return
	# match code from requested token pool
	code = params
	q = db.GqlQuery( "SELECT * FROM OAuthRequest "
				"WHERE code = :1 ", code)
	e = q.get()
	if e is None:
		r.l("!code mismatched")
		return
	
	# load required data
	uid = e.user_id
	a_token = e.access_token
	a_secret = e.access_secret

	# remove data relevant to uid from token pool
	q = db.GqlQuery( "SELECT * FROM OAuthRequest "
				"WHERE user_id = :1 ", uid)
	for e in q:
		e.delete()
	
	# search if uid has stored in User
	q = db.GqlQuery( "SELECT * FROM User "
				"WHERE uid = :1 ", uid)
	user_entity = q.get()
	if user_entity is None:
		user_entity = User(
			uid = uid,
			a_token = a_token,
			a_secret = a_secret) 
	else:
		user_entity.a_token = a_token
		user_entity.a_secret = a_secret
	user_entity.put()
	# User stored
	q = db.GqlQuery( "SELECT * FROM Account "
				"WHERE account = :1 ", account)
	acc_entity = q.get()
	if acc_entity is None:
		acc_entity = Account(account = account)
	acc_entity.active_id = uid
	acc_entity.put()
	# Account stored
	q = db.GqlQuery( "SELECT * FROM RelationAccountUser "
				"WHERE account = :1 AND user = :2 ",
			acc_entity,
			user_entity)
	e = q.get()
	if e is None:
		e = RelationAccountUser(
			account = acc_entity, 
			user = user_entity)
		e.put()
	# Relation Stored
	r.l( "bind done" )

def cmdUser(account, params, r):
	"""
		# account
		% list avaliable users
		% format: .user

		* only users that have connection with account
		* can be seen
	"""
	if len( params ) > 0:
		r.l("!bad argument")
		return

	acc_entity = twig_db.getAccount(account)
	query = db.GqlQuery( "SELECT * FROM RelationAccountUser "
			"WHERE account = :1 ", acc_entity )
	user_list = []
	for e in query:
		user_list.append( e.user.uid )
	
	r.l("%d user(s) are found" % len(user_list))
	r.l( ("active_id", acc_entity.active_id) )
	r.l( user_list )
	
# XXX : support screen_name switch in future
def cmdSwitch(account, params, r):
	"""
		# account
		% switch to another user
		% format: .switch [user_id]
		% leaving user_id blank leads to command ".user"
	"""
	if len(params) == 0:
		return cmdUser(account, params, r)
	acc_entity = twig_db.getAccount(account)
	user_entity = twig_db.getUser(params)
	
	query = db.GqlQuery( "SELECT * FROM RelationAccountUser "
			"WHERE account = :1 AND user = :2 ",
			acc_entity, user_entity)
	e = query.get()
	if e is None:
		r.l("!cannot find this user")
		return

	acc_entity.active_id = user_entity.uid
	acc_entity.put()
	r.l("switch done")

def cmdUnBind(account, params, r):
	"""
		# account
		% remove user
		% format: .unbind [user_id]
		% leaving user_id blank leads to command ".user"
	"""
	# break relation between account and a user
	if len(params)==0:
		return cmdUser(account, params, r)
	
	acc_entity = twig_db.getAccount(account)
	user_entity = twig_db.getUser(params)
	
	query = db.GqlQuery( "SELECT * FROM RelationAccountUser "
			"WHERE account = :1 AND user = :2 ",
			acc_entity, user_entity)
	e = query.get()
	if e is None:
		r.l("!cannot find this user")
		return
	
	if acc_entity.active_id == user_entity.uid:
		acc_entity.active_id = None
		acc_entity.put()
		r.l( "warn: active user removed")
	e.delete()
	r.l("user removed")

import command
import twig_command
import twitter_command
import tools

def cmdHelp(account, params, r):
	"""
		# help
		% get help about commands
		% format: .help [cmd]
		% cmd is the command name without leading '.'
		% e.g: .help bind
		% leaving cmd blank prints this message

		this command grabs and filters functions/methods' __doc__ directly
		  and '# <category>' will assign a category for the command,
		  any line with a leading '% ' will be interpreted as help document
		  and returned to the user.
	"""
	if len(params) == 0:
		params = 'help'
	f = command.lookForCommand( params )
	if f is None:
		r.l("!no such command")
		return
	try:
		cmdAlias(account, params, r)
		cmdCommandCategory(account, params, r)
		helps = re.findall( r"% (.*)$", f.__doc__, re.MULTILINE )
		map( r.l, helps ) 
	except:
		r.l("!no help found")

def cmdAlias(account, params, r):
	"""
		# help
		% get alias of a give command
		% format: .alias <cmd>
		% cmd is the command name without leading '.'
		% e.g.: .alias @
		% a list will be returned:
		% # alias:
		% A [@,at,mention]
		% which means '.@' '.at' and '.mention' are all identical
		* when called as function, return the alias list
	"""
	if len( params ) == 0:
		r.l("!bad argument")
		return
	table = {}
	table.update( twitter_command.alias_table )
	table.update( twig_command.alias_table )
	cmd = tools.translate( params, table )
	alist = [cmd]
	for k, v in table.iteritems():
		if v == cmd:
			alist.append( k )
	alist.sort()
	r.l( ("cmd", cmd) )
	r.l( "alias:" )
	r.l( alist )
	return alist

def cmdWhere(account, params, r):
	"""
		# help
		% print help document about [where]
		% 'where' is a tweet id, leading with special characters
		% character '<' means tweets newer than the given tweet
		% character '>' means tweets older than the given tweet
		% 
		%   [<] --->time-->(tweet id)--->time---> [>]
		%                      
		% e.g.: 
		%   1) ".ho <12345" means "show me home timeline, 
		%      tweets of which are newer than the tweet that has id '12345' "
		%   2) ".@ >654321" means "show me mentions timeline,
		%      tweets of which are older than the tweet that has id '54321' "
		% * the leading character MUST be one of '<' or '>' 
		%   and followed by tweet id immediately WITHOUT any whitespace
	"""
	if len( params )>0:
		r.l("!bad argument")
		return
	cmdHelp(account, "where", r)

def cmdLengthCheck(account, params, r):
	"""
		# help 
		% check if text length is greater than 140 chars
		% return NOTHING if length check passed
		% return truncated strings' length and content on failure 
		% format: .lengthcheck <text> 
		% * all tweets you intend to send are all judged 
		%   automatically by this command
		* when called as a function, it returns the shorten text
	"""
	if len( params ) > 140:
		text, rest = params[:139] + u"…", params[139:]
		r.l("warning: text truncated, print rest text")
		r.l( ("len", len(rest)) )
		r.l( ( "[%s]" % rest ) )
		return text
	return params

def cmdVersion(account, params, r):
	"""
		# help
		% check twig version
		% format: .version
	"""
	if len( params ) > 0:
		r.l("!bad argument")
		return
	from version import VERSION
	r.l( ("version", VERSION) )

import re
import inspect
def cmdCommandList(account, params, r):
	"""
		# help
		% make a list of available commands
		% format: .commandlist
	"""
	if len( params ) > 0:
		r.l("!bad argument")
		return
	command_list = []

	valid_function = lambda f: \
				inspect.isfunction(f) and \
				f.__name__[:3] == 'cmd' and \
				f.__name__[3:] != ''
	func_list = inspect.getmembers( twig_command, valid_function )
	command_list += map ( lambda item: item[0][3:].lower(), func_list )

	valid_method = lambda m: \
				inspect.ismethod(m) and \
				m.__name__[:6] == 'twiCmd' and \
				m.__name__[6:] != ''
	meth_list = inspect.getmembers( twitter_command.TwitterAPIWrapper, valid_method )
	command_list += map ( lambda item: item[0][6:].lower(), meth_list )
	
	command_list = sorted( command_list )
	map( lambda cmd: r.l ( cmd ), command_list )
	
def cmdCommandCategory(account, params, r):
	"""
		# help
		% get category of a specific command
		% format: .commandcategory <cmd>
	"""
	if len(params)==0:
		r.l("!bad argument")
		return
	from category import getCategory
	c, d = getCategory(params)
	if c is None:
		r.l("!command not found")
		return

	r.l( ("category", d) )
		
# idea grabbed from http://stackoverflow.com/questions/4201062/how-can-i-unshorten-a-url-using-python
def cmdUnshortLink(account, params, r):
	"""
		% unshort links
		% format: .unshort <link>
		
		* make use of unshort.me
	"""
	if len(params)==0:
		r.l("!bad argument")
		return
	url = 'http://api.unshort.me/?r=%s&t=json' % params 
	try:
		f = urllib2.urlopen( url )
		data = json.load( f )
		if data["success"] != "true":
			r.l("!unshort failed")
			return
		r.r( data["resolvedURL"] )
		return
	except:
		r.l( "!unshort failed" )
