# -*- coding: utf-8 -*-

from twig_db import getUserInfo, getActiveUser
from pyoauth4twitter.oauth_twitter import TwitterConsumer, TwitterRequest
from oauth import CONSUMER_SECRET, CONSUMER_KEY
from tools import urlesc
import json
import twitter_object
import tools
import re
from tools import mkURL, urlMix
import twig_command

# key, value = alias, cmd 
alias_table = {
	"at" :		"mention",
	"@" :		"mention",
	"dm" :		"directmessage",
	"d<":		"directmessage",
	"din":		"directmessage",
	"dsent":	"directmessagesent",
	"dout":		"directmessagesent",
	"d>":		"directmessagesent",
	"d":		"directmessagenew",
	"d+":		"directmessagenew",
	"d-":		"directmessagedestroy",
	"ddel":		"directmessagedestroy",
	"send":		"update",
	"ho":		"hometimeline",
	"home":		"hometimeline",
	"fo":		"follow",
	"uf":		"unfollow",
	"unfo":		"unfollow",
	"b":		"block",
	"fuck":		"block",
	"ub":		"unblock",
	"if":		"checkrelation",
	"cr":		"checkrelation",
	"chkrel":	"checkrelation",
	"rpy":		"reply",
	"rp":		"reply",
	"rpya":		"replyall",
	"rpa":		"replyall",
	"@a":		"replyall",
	"st":		"status",
	"r":		"retweet",
	"rt":		"retweetwithcomment",
	"delete":	"destroy",
	"del":		"destroy",
	"rm":		"destroy",
	"fav":		"favorite",
	"lsfav":	"favorite",
	"+fav":		"favoritecreate",
	"fav+":		"favoritecreate",
	"fadd":		"favoritecreate",
	"-fav":		"favoritedestroy",
	"fav-":		"favoritedestroy",
	"fdel":		"favoritedestroy",
	"frm":		"favoritedestroy",
	"unfav":	"favoritedestroy",
	"me":		"mytweets",
	"tl":		"usertimeline",
	"msg":		"conversation",
	"bt":		"conversation",
	"backtrack":	"conversation",
	"s":		"search",
	"lsm":		"list",
	"lssub":	"listsubscription",
	"lt":		"listsubscription",
	"lsmem":	"listmembership",
	"lsmbr":	"listmembership",
	"ld":		"listmembership",
	"ls":		"liststatus"
}

class TwitterAPIWrapper(object):
	"""
		twitter api wrapper, provide context for commands
		that requires twitter authorization
	"""

	def __init__(self, account):
		"""
			need account name to initialize this class
			fed with all keys necessary, I will get ready to sign requests
		"""
		self.account = account
		a_token, a_secret, self.uid = getUserInfo(account)
		self.tc = TwitterConsumer(CONSUMER_KEY, CONSUMER_SECRET)
		self.tc.for_user(a_token, a_secret)

	def post(self, url, r):
		"""
			shortcut for post requests
			return (True, response) on success, 
			and return (False, response) on failure
			explanation of errors will be written on 'r'
		"""
		tr = TwitterRequest("POST", url )
		response = self.tc.get_response( tr )
		return (self._judgeStatus( response, r ), response)

	def get(self, url, r):
		"""
			shortcut for get requests
			return (True, response) on success, 
			and return (False, response) on failure
			explanation of errors will be written on 'r'
		"""
		tr = TwitterRequest("GET", url )
		response = self.tc.get_response( tr )
		return (self._judgeStatus( response, r ), response)

	def _parseList(self, raw, builder):
		"""
			parse items in list into classes
			raw: raw json data
			builder: function that reads data and products a corresponding class
			* list will be reversed for reading conveniences
		"""
		jdata = json.loads( raw )
		result = map(builder, jdata)
		result.reverse()
		return result

	def _judgeStatus(self, response, r):
		"""
			read, judge status
			on success:
			  return True
			on failure:
			  return False, and write explantion to "r"
		"""
		if (response.status!= 200):
			r.l( ("status", response.status) )
			if response.status == 404:
				return
			err_info = json.loads( response.read() )
			try:
				r.l( '!%s' % err_info["errors"][0]["message"] )
			except:
				try:
					r.l( "!%s" % err_info["errors"] )
				except:
					r.l( '!something went wrong...' )
					r.l( unicode( err_info ) )

			return False
		else:
			return True
		

	def twiCmdUpdate(self, params, r):
		"""
			# ttweet
			% send a new tweet
			% format: .update <text>
			% simply type in messages leading with anything but '.'
			% will send tweets as well, for messages leading with '.'
			% duplicating '.' will make it
			% e.g. "..net is good!" products ".net is good!"
		"""
		params = twig_command.cmdLengthCheck(None, params, r) 
		url = mkURL("https://api.twitter.com/1.1/statuses/update.json", status=params)
		succ, response = self.post(url, r)
		if not succ:
			return
		r.l( "sent" )

	def twiCmdHomeTimeline(self, params, r):
		"""
			# ttweet
			% show my home timeline
			% format: .ho [where]
			% use command '.where' for how to use '[where]'
		"""
		extra = tools.parseWhere( params )
		if extra is None:
			r.l("!bad page argument")
			return
		url = mkURL( "https://api.twitter.com/1.1/statuses/home_timeline.json", **extra )
		succ, response = self.get(url, r)	
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.Tweet )
		r.l( tl )

	def twiCmdMention(self, params, r):
		"""
			# ttweet
			% show my mentions timeline
			% * if you are seeking help for how to reply others,
			%   please refer to '.help reply'
			% format: .mention [where]
			% use command '.where' for how to use '[where]'
		"""
		extra = tools.parseWhere( params )
		if extra is None:
			# there is another form of reply, jump to it.
			self.twiCmdReply( params, r )
			return

		url = mkURL( "https://api.twitter.com/1.1/statuses/mentions_timeline.json", **extra )
		succ, response = self.get(url, r)	
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.Tweet )
		r.l( tl )

	def twiCmdReply(self, params, r):
		"""
			# ttweet
			% reply only to the author of a given tweet
			% * if you want to reply all users mentioned in a tweet,
			%   please refer to '.help replyall'
			% format: .reply <id> <text>
			% e.g.: .reply 123456 I'm fine thank you, and you?
		"""
		pat = re.compile(r'^(\d+)(?:\s+)(.*)$')
		m = pat.match( params )
		if m is None:
			r.l( "!bad argument")
			return
		tid, text = m.group(1), m.group(2) 

		# at first we should find this tweet ...
		url = "https://api.twitter.com/1.1/statuses/show/%s.json" % tid
		succ, response = self.get( url, r )
		if not succ:
			r.l( "!failed when fetching origin tweet" )
			return
		user = json.loads( response.read() )["user"]["screen_name"]
		text = "@%s %s" % (user, text)
		text = twig_command.cmdLengthCheck( None, text, r)

		# now send text!
		url = mkURL( "https://api.twitter.com/1.1/statuses/update.json", status=text, in_reply_to_status_id=tid)
		succ, response = self.post( url, r )
		if not succ:
			r.l("!failed when sending reply")
			return
		
		r.l( "replied to %s" % user )
		 
	def twiCmdReplyAll(self, params, r):
		"""
			# ttweet
			% reply to all users mentions in a given tweet
			% * if you want to reply only to the author of a tweet,
			%   please refer to '.help reply'
			% format: .replyall <id> <text>
			% e.g.: .replyall 123456 I'm fine thank you, and you?
		"""
		pat = re.compile(r'^(\d+)(?:\s+)(.*)$')
		m = pat.match( params )
		if m is None:
			r.l( "!bad argument")
			return
		tid, text = m.group(1), m.group(2) 

		# at first we should find this tweet ...
		url = "https://api.twitter.com/1.1/statuses/show/%s.json" % tid
		succ, response = self.get( url, r )
		if not succ:
			r.l( "!failed when fetching origin tweet" )
			return
		data = json.loads( response.read() ) 
		# metion list build: mention list should contain author
		# and all users mentioned except you
		author = data["user"]["screen_name"]
		# make use of "entities" to find users mentioned
		user_list = data["entities"]["user_mentions"]
		# let's filter out myself and transform it into a list
		# that contains screen name only
		user_list = filter ( lambda user: user["id_str"] != self.uid, user_list)
		user_list = map (lambda user: "@"+user["screen_name"], user_list )
		user_list.append( "@" + author )
		user_list = sorted( list( set( user_list ) ) )

		text = "%s %s" % (' '.join(user_list), text)
		text = twig_command.cmdLengthCheck( None, text, r)
		# ok I'm ready to send
		url = mkURL( "https://api.twitter.com/1.1/statuses/update.json", status=text, in_reply_to_status_id=tid)
		succ, response = self.post( url, r )
		if not succ:
			r.l("!failed when sending reply")
			return
		
		r.l( "replied to %s" % ' '.join( map(lambda t: t[1:], user_list) ) )
	
	def twiCmdDirectMessage(self, params, r):
		"""
			# tdm
			% view received direct messages (inbox)
			% format: .dm [where]
			% use command '.where' for how to use '[where]'

		"""
		extra = tools.parseWhere( params )
		if extra is None:
			r.l("!bad page argument")
			return
		url = mkURL ( "https://api.twitter.com/1.1/direct_messages.json", **extra )
		succ, response = self.get( url, r )	
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.DirectMessage )
		r.l( tl )

	def twiCmdDirectMessageSent(self, params, r):
		"""
			# tdm
			% view sent direct messages (outbox)
			% format: .dout [where]
			% use command '.where' for how to use '[where]'

		"""
		extra = tools.parseWhere( params )
		if extra is None:
			r.l("!bad page argument")
			return
		url = mkURL ( "https://api.twitter.com/1.1/direct_messages/sent.json", **extra )
		succ, response = self.get( url, r )	
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.DirectMessage )
		r.l( tl )

	def twiCmdDirectMessageNew(self, params, r):
		"""
			# tdm
			% send direct message
			% * if you want help of checking received direct message
			%   please refer to ".dm"
			% format: .d <user> <message>
		"""
		pat = re.compile(r"([A-Za-z0-9_]+)\s+(.*)")
		m = pat.match( params )
		if m is None:
			# user might want to check inbox by this command
			self.twiCmdDirectMessage( params, r )
			return
		usr, text = m.groups()
		url = mkURL( "https://api.twitter.com/1.1/direct_messages/new.json", screen_name=usr, text=text)
		succ, response = self.post( url, r )
		if not succ:
			return
		r.l( "direct message sent" )

	def twiCmdDirectMessageDestroy(self, params, r):
		"""
			# tdm
			% delete a direct message
			% format: .d- <direct message id>
		"""
		if not params.isdigit():
			r.l( "!bad argument" )
			return

		url = mkURL( "https://api.twitter.com/1.1/direct_messages/destroy.json", id=params )
		succ, response = self.post( url, r)
		if not succ:
			return
		r.l( "direct message removed" )
		
	def twiCmdFollow(self, params, r):
		"""
			# tfriend
			% follow user
			% format: .fo <user>
		"""
		# XXX: potential injection
		url = mkURL( "https://api.twitter.com/1.1/friendships/create.json", screen_name = params )
		succ, response = self.post( url, r )
		if not succ:
			return
		name = json.loads( response.read() )["screen_name"]
		r.l("followed %s" % name)

	def twiCmdUnFollow(self, params, r):
		"""
			# tfriend
			% un-follow user
			% format: .unfo <user>
		"""
		# XXX: potential injection
		url = mkURL( "https://api.twitter.com/1.1/friendships/destroy.json", screen_name = params )
		succ, response = self.post( url, r )
		if not succ:
			return
		name = json.loads( response.read() )["screen_name"]
		r.l("un-followed %s" % name)

	def twiCmdBlock(self, params, r):
		"""
			# tfriend
			% block user
			% format: .block <user>
		"""
		# XXX: potential injection
		url = mkURL( "https://api.twitter.com/1.1/blocks/create.json", screen_name = params )
		succ, response = self.post( url, r )
		if not succ:
			return
		name = json.loads( response.read() )["screen_name"]
		r.l("blocked %s" % name)

	def twiCmdUnBlock(self, params, r):
		"""
			# tfriend
			% un-block user
			% format: .unblock <user>
		"""
		# XXX: potential injection
		url = mkURL( "https://api.twitter.com/1.1/blocks/destroy.json", screen_name = params )
		succ, response = self.post( url, r )
		if not succ:
			return
		name = json.loads( response.read() )["screen_name"]
		r.l("un-blocked %s" % name)

	def twiCmdCheckRelation(self, params, r):
		"""
			# tfriend
			% check relationship between you and another twitter user
			% format: .checkrelation <user>
			% * 'friends' means you are following muturally
		"""
		# XXX: potential injection
		url = mkURL( "https://api.twitter.com/1.1/friendships/lookup.json", screen_name = params )
		succ, response = self.get( url, r )
		if not succ:
			return
		ppl_list = json.loads( response.read() )
		if len(ppl_list) == 0:
			r.l( "!cannot find this user" )
			return
		
		ppl = ppl_list[0]
		if ppl["id_str"] == self.uid:
			r.l( "it's you!" )
			return

		if "none" in ppl["connections"]:
			r.l( "%s has no connection with you" % ppl["screen_name"] )
			return

		if len( ppl["connections"] ) == 2:
			r.l( "%s and you are friends" % ppl["screen_name"])
			return

		if "following" in ppl["connections"]:
			r.l( "you are following %s" % ppl["screen_name"])
			return

		if "followed_by" in ppl["connections"]:
			r.l( "you are followed by %s" % ppl["screen_name"])
			return

		r.l( "relationship check failed" )
	
	def twiCmdStatus(self, params, r):
		"""
			# tfriend
			% get information about a user
			% format: .status [user]
			% when user is not given, the status of you will be shown
			% MIGHT return the most recent status, if any
		"""
		url = "https://api.twitter.com/1.1/users/show.json" 
		if len(params) > 0:
			url = mkURL( url, screen_name = params )
		else:
			url = mkURL( url, user_id = self.uid )
		succ, response = self.get( url, r )
		if not succ:
			return
		data = json.loads( response.read() )
		
		map( lambda key: (r.l(key), r.r(data[key])), 
			[
				"name",
				"location",
				"description",
			]			
		)
		map( lambda key: r.l( (key, data[key])),
			[
				"screen_name",
				"id",
				"statuses_count",
				"friends_count",
				"followers_count",
			]
		)
		try:
			recent = data["status"]["text"]
			r.l( "status" )
			r.r( recent )
		except:
			pass

		if len(params) > 0:
			self.twiCmdCheckRelation(params, r)

	def twiCmdRetweet(self, params, r):
		"""
			# ttweet
			% official retweet, cannot add your comment
			% if you want help of 'retweet with comment'
			% please refer to .rt
			% format: .r <tweet id>
			% * you can add your comment after the tweet_id
			%   but by doing this, this command will act like ".rt"
			% e.g. : 
			%   1)  ".r 123456" retweets tweet that has id 123456
			%   2)  ".r 123456 comment" is identical to ".rt 123456 comment"
		"""
		if not params.isdigit():
			# jump to 'rt', which allows comments
			self.twiCmdRetweetWithComment(params, r)
			return
		url = "https://api.twitter.com/1.1/statuses/retweet/%s.json" % params
		succ, response = self.post( url, r)
		if not succ:
			return
		r.l( "official retweeted" )

	def twiCmdRetweetWithComment(self, params, r):
		"""
			# ttweet
			% retweet with your comment, differ from the offical retweet
			% format: .rt <tweet id> [your comment]
		"""
		pat = re.compile("(\d+)(?:(?:\s+)(.*))?$")
		m = pat.match( params )
		if m is None:
			r.l("!bad argument")
			return
		tid, text = m.group(1), m.group(2)

		# collection origin author name...
		url = "https://api.twitter.com/1.1/statuses/show/%s.json" % tid
		succ, response = self.get( url, r )
		if not succ:
			r.l( "!failed when fetching origin tweet" )
			return
		data = json.loads( response.read() ) 
		author = data["user"]["screen_name"]
		
		if text is None:
			text = "RT @%s: %s" % (author, data["text"])
		else:
			text = "%s RT @%s: %s" % (text, author, data["text"])
		
		text = twig_command.cmdLengthCheck(None, text, r) 
		url = mkURL("https://api.twitter.com/1.1/statuses/update.json", status=text, in_reply_to_status_id=tid)
		succ, response = self.post(url, r)
		if not succ:
			return
		r.l( "retweeted" )

	def twiCmdDestroy(self, params, r):
		"""
			# ttweet
			% remove a specific or the most recent tweet you've sent
			% format: .del [id]
			% if id is not given, I will delete the most recent one.
		"""
		if len( params ) > 0 and not params.isdigit():
			r.l("!bad argument")
			return
		if len( params ) == 0:
			# now I have to find the last tweet you've sent
			url = mkURL( "https://api.twitter.com/1.1/users/show.json", user_id = self.uid )
			succ, response = self.get( url, r )
			if not succ:
				r.l( "!failed when fetching origin tweets" )
				return
			data = json.loads( response.read() )
			try:
				tid = data["status"]["id_str"]
			except:
				r.l( "!you don't have any tweet" )
				return
		else:
			tid = params

		url = mkURL( "https://api.twitter.com/1.1/statuses/destroy/%s.json" % tid )
		succ, response = self.post( url, r)
		if not succ:
			return
		r.l("removed")

	def twiCmdFavorite(self, params, r):
		"""
			# tfav
			% view tweets favorited by you or a specific user
			% format: .fav [user] [where]
			% both 'user' and 'where' are optional
			% if 'user' is not given, I will grab the favorate list of you.
			% use command '.where' for how to use '[where]'
		"""
		para_list = params.split()
		query = {}
		if len( para_list ) > 2:
			r.l("!bad argument")
			return
		if len( para_list ) == 0:
			# view favorite tweets of yourself
			query["user_id"] = self.uid
		elif len( para_list ) == 2:
			w = tools.parseWhere( para_list[1] )
			if w is None:
				r.l("!bad argument")
				return
			query.update(w)
			query["screen_name"] = para_list[0]
		else:
			# only 1 element in the list
			# which must be either [user] or [where]
			w = tools.parseWhere( para_list[0] )
			if w is None:
				# this is actually a user name
				query["screen_name"] = para_list[0]
			else:
				# this is a 'where' 
				query.update(w)
				query["user_id"] = self.uid
		url = mkURL( "https://api.twitter.com/1.1/favorites/list.json", **query )
		succ, response = self.get( url, r)
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.Tweet )
		r.l( tl )

	def twiCmdFavoriteCreate(self, params, r):
		"""
			# tfav
			% mark tweets as favorate
			% format: .+fav <tweet id>
		"""
		if not params.isdigit():
			r.l("!bad argument")
			return
		url = mkURL( "https://api.twitter.com/1.1/favorites/create.json", id=params )
		succ, response = self.post( url, r )
		if not succ:
			return
		r.l ( "favorited" ) 

	def twiCmdFavoriteDestroy(self, params, r):
		"""
			# tfav
			% remove tweets from favorite list
			% format: .-fav <tweet id>
		"""
		if not params.isdigit():
			r.l("!bad argument")
			return
		url = mkURL( "https://api.twitter.com/1.1/favorites/destroy.json", id=params )
		succ, response = self.post( url, r )
		if not succ:
			return
		r.l ( "un-favorited" ) 

	def twiCmdMyTweets(self, params, r):
		"""
			# ttweet
			% get my tweets
			% format: .me [where]
			% use command '.where' for how to use '[where]'
		"""
		extra = tools.parseWhere( params )
		if extra is None:
			r.l( "!bad argument" )
			return
		extra["user_id"] = self.uid
		url = mkURL( "https://api.twitter.com/1.1/statuses/user_timeline.json", **extra )
		succ, response = self.get( url, r )
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.Tweet )
		r.l( tl )

	def twiCmdUserTimeline(self, params, r):
		"""
			# ttweet
			% view timeline of a given user
			% format: .tl [user] [where] 
			% both 'user' and 'where' are optional
			% 'user' is you by default
			% use command '.where' for how to use '[where]'
		"""
		para_list = params.split()
		query = {}
		if len( para_list ) > 2:
			r.l( "!bad argument" )
		if len( para_list ) == 0:
			# identical to '.me'
			self.twiCmdMyTweets( params, r )
			return
		if len( para_list ) == 1:
			if para_list[0][0] in '<>':
				# identical to '.me'
				self.twiCmdMyTweets( params, r)
				return
			else:
				# is a user
				query["screen_name"] = para_list[0]
		else:
			# has both user and 'where'
			extra = tools.parseWhere( para_list[1] )
			if extra is None:
				r.l ( "!bad argument" )
				return
			query.update( extra )
			query["screen_name"] = para_list[0]
		# query is ready
		url = mkURL("https://api.twitter.com/1.1/statuses/user_timeline.json", **query)
		succ, response = self.get( url, r )
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.Tweet )
		r.l( tl )

	def twiCmdConversation(self, params, r):
		"""
			# ttweet
			% view conversation, backtrack tweets
			% format: .msg <tweet id>
			% up to 5 tweets
			* modify BACKTRACK_LIMIT and this comment 
			  if you want a stronger/weaker backtracking ability
		"""
		BACKTRACK_LIMIT = 5
		
		if not params.isdigit():
			r.l("!bad argument")
			return

		bt_count = 0
		tid = params
		tweets = []
		while bt_count < BACKTRACK_LIMIT and tid is not None:
			bt_count += 1
			url = "https://api.twitter.com/1.1/statuses/show/%s.json" % tid
			succ, response = self.get( url, r )
			if not succ:
				break
			tweet = json.loads( response.read() )
			tweets.append( tweet )
			tid = tweet["in_reply_to_status_id_str"]
		tweets = map( twitter_object.Tweet, tweets )
		tweets.reverse()
		r.l( tweets )
		if tid is None:
			r.l( "origin tweet reached" )
		else:
			r.l( "backtrack limit reached" )
	
	def twiCmdSearch(self, params, r):
		"""
			# ttweet
			% search tweets
			% format: .s "<query>" [where]
			% query can contain any characters including whitespace
			% use command '.where' for how to use '[where]'
			% e.g:  .s "bob and alice" <123456
		"""
		pat = re.compile( r'"(.*)"(\s+([<|>]\d+))?' )
		m = pat.match( params )
		if m is None:
			r.l( "!bad argument" )
			return
		q, _, where = m.groups()
		if where is None:
			where = ''
		query = tools.parseWhere( where )
		query["q"] = q
		url = mkURL( "https://api.twitter.com/1.1/search/tweets.json", **query)
		succ, response = self.get( url, r )
		if not succ:
			return
		data = json.loads( response.read() )["statuses"]
		tl = map( twitter_object.Tweet, data )
		tl.reverse()
		r.l( tl )

	def twiCmdList(self, params, r):
		"""
			# tlist
			% return all lists you subscribes to
			% format: .lsm
		"""
		url = "https://api.twitter.com/1.1/lists/list.json"
		succ, response = self.get( url, r )
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.ListInfo )
		r.l( tl )

	def twiCmdListSubscription(self, params, r):
		"""
			# tlist
			% show lists you are subscribed to
			% format: .lssub [cursor]
			% cursor will be given in the result of this command
			% use number in 'next' to lead you to the next page
			% and number in 'prev' to the previous page
		"""
		cursor = {}
		if len( params ) > 0:
			try:
				cursor["cursor"] = int ( params )
			except:
				r.l( "!bad argument" )
				return

		url = mkURL( "https://api.twitter.com/1.1/lists/subscriptions.json", **cursor )
		succ, response = self.get( url, r )
		if not succ:
			return
		data = json.loads( response.read() )
		lists = data["lists"]
		r.l( map( twitter_object.ListInfo, lists ) )
		r.l( ("next", data["next_cursor_str"]) )
		r.l( ("prev", data["previous_cursor_str"]) )

	def twiCmdListMembership(self, params, r):
		"""
			# tlist
			% show lists you have been added to
			% format: .lsmbr [cursor]
			% cursor will be given in the result of this command
			% use number in 'next' to lead you to the next page
			% and number in 'prev' to the previous page
		"""
		cursor = {}
		if len( params ) > 0:
			try:
				cursor["cursor"] = int ( params )
			except:
				r.l( "!bad argument" )
				return

		url = mkURL( "https://api.twitter.com/1.1/lists/memberships.json", **cursor )
		succ, response = self.get( url, r )
		if not succ:
			return
		data = json.loads( response.read() )
		lists = data["lists"]
		r.l( map( twitter_object.ListInfo, lists ) )
		r.l( ("next", data["next_cursor_str"]) )
		r.l( ("prev", data["previous_cursor_str"]) )

	def twiCmdListStatus(self, params, r):
		"""
			# tlist
			% show tweets in a given list
			% format: .ls <list id> [where]
			% use command '.where' for how to use '[where]'
		"""
		params = params.split()
		if len( params ) == 0:
			r.l("!bad argument")
			return
		if not params[0].isdigit():
			r.l("!bad argument")
			return
		if len( params ) == 2:
			extra = tools.parseWhere( params[1] )
			if extra is None:
				r.l("!bad page argument")
				return
		assert extra is not None
		extra["list_id"] = params[0]
		url = mkURL( "https://api.twitter.com/1.1/lists/statuses.json", **extra )
		succ, response = self.get(url, r)	
		if not succ:
			return
		raw_data = response.read()
		tl = self._parseList( raw_data, twitter_object.Tweet )
		r.l( tl )

