import webapp2
from google.appengine.api import xmpp
from google.appengine.ext import db
import command
import twig_db
from reply import Reply

class ChatHandler(webapp2.RequestHandler):
	def post(self):
		# parse message
		message = xmpp.Message(self.request.POST)
		raw_text = message.body
		account = message.sender.split('/')[0].lower()
		# find active user of this account
		uid = twig_db.getActiveUser(account)

		r = Reply()
		isCmd, data = command.parseText( raw_text )	
		if isCmd:
			# is command
			cmd, params = data
			command.dispatchCommand(account, cmd, params, r)
			if len( r.o ) > 0:
				message.reply( r.o )
		else:
			# is text
			if uid:
				command.dispatchCommand(account, 'send', data, r) 
				message.reply( r.o )
			else:
				r.l( "!no active user found")
				message.reply( r.o )

class PresenceHandler(webapp2.RequestHandler):
	def post(self):
		sender = self.request.get('from').split('/')[0]
		acc_entity = twig_db.getAccount( sender )
		if acc_entity is None:
			return
		q = db.GqlQuery( "SELECT * FROM RelationAccountUser "
					"WHERE account = :1 ", acc_entity )
		text = ".h <cmd> for help, %d users available" % q.count()
		xmpp.send_presence(sender, status=text)

class NullHandler(webapp2.RequestHandler):
	def post(self):
		pass

app = webapp2.WSGIApplication(
		[
			(r'/_ah/xmpp/message/chat/', 		ChatHandler),
			(r'/_ah/xmpp/presence/available/', 	PresenceHandler),
			(r'/_ah/xmpp/presence/probe/', 		PresenceHandler),
			(r'/_ah/xmpp/presence/.*', 		NullHandler),
		], 
		debug=True)
