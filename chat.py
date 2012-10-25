import webapp2
from google.appengine.api import xmpp
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
			message.reply( r.o )
		else:
			# is text
			if uid:
				command.dispatchCommand(account, 'send', data, r) 
				message.reply( r.o )
			else:
				r.l( "!no active account found")
				message.reply( r.o )

app = webapp2.WSGIApplication(
		[
			('/_ah/xmpp/message/chat/', ChatHandler)
		], 
		debug=True)
