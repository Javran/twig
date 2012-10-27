import webapp2
from google.appengine.api.app_identity import get_application_id
import tools
from pyoauth4twitter.oauth_twitter import TwitterConsumer, TwitterRequest
from google.appengine.ext import db
import random
from twig_db import OAuthRequest
from config import CONSUMER_KEY, CONSUMER_SECRET, REQUIRE_INVITATION
from invite import removeInvitation
import tools

CALLBACK_URL = 'http://%s.appspot.com/oauth/callback' % get_application_id()

class OAuthSignHandler(webapp2.RequestHandler):
	def get(self):
		err_msg = self.request.get("error", default_value="")
		tools.loadHead( self.response )
		html = tools.parseMarkdown("./page_src/sign.md", {
				"{{app_name}}" : get_application_id(),
				"{{error_msg}}" : err_msg })
		self.response.write(html)
	
class OAuthRequestTokenHandler(webapp2.RequestHandler):
	def get(self):

		if REQUIRE_INVITATION:
			code = self.request.get("code", default_value="")
			if not removeInvitation( code ):
				self.redirect( "/oauth/sign?error=Invalid%20invitation%20code" )
				# self.response.write("Invalid invitation code, authorization aborted.")
				return

		tc = TwitterConsumer(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL) 
		tc.request_token()

		entity = OAuthRequest(token=tc.token)
		entity.token_secret = tc.token_secret
		entity.put()
		#self.response.write("addr: https://api.twitter.com/oauth/authenticate?oauth_token=%s" % tc.token)
		self.redirect( "https://api.twitter.com/oauth/authorize?oauth_token=%s&force=1" % tc.token )

class OAuthCallbackHandler(webapp2.RequestHandler):
	def get(self):
		token = self.request.get('oauth_token')
		verifier = self.request.get('oauth_verifier')
		
		# find token in database...
		query = db.GqlQuery( 
			"SELECT * "
				"FROM OAuthRequest "
				"WHERE token = :1 ",
			token)
		entity = query.get()
		if entity is None:
			self.response.write("error: cannot find")
			return

		# prepare for obtaining access_token
		tc = TwitterConsumer(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
		tc.token = entity.token
		tc.token_secret = entity.token_secret
		tc.verifier = verifier
		
		# obtain access token
		tc.access_token()
		
		if not tc.has_user():
			self.response.write("failed when verifying.")
			return

		entity.user_id = tc.user_id
		entity.access_token = tc.a_token
		entity.access_secret = tc.a_secret
		
		# dump all codes
		query = db.GqlQuery(
			"SELECT code "
				"FROM OAuthRequest ")
		code_list = []
		for e in query:
			if e.code is not None:
				code_list.append( int(e.code) )

		# select one unique code as PIN
		code = random.randint(0, 999999)
		while code in code_list:
			code = random.randint(0, 999999)

		entity.code = "%06d" % code
		entity.put()
		#self.response.write("use code: %s to bind your gtalk." % entity.code )
		self.redirect( "/oauth/finish?code=%s" % entity.code )

class OAuthFinishHandler(webapp2.RequestHandler):
	def get(self):
		tools.loadHead( self.response )

		code = self.request.get("code")
		html = tools.parseMarkdown( "./page_src/finish.md", {
			"{{app_name}}" : get_application_id(),
			"{{code}}": code})
		#self.response.write("use code: %s to bind your gtalk." % code )
		self.response.write(html)

app = webapp2.WSGIApplication(
		[
			('/oauth/sign', 		OAuthSignHandler),
			('/oauth/request_token', 	OAuthRequestTokenHandler),
			('/oauth/callback', 		OAuthCallbackHandler),
			('/oauth/finish', 		OAuthFinishHandler),
		], 
		debug=True)
