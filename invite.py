import webapp2
from google.appengine.api.app_identity import get_application_id
from google.appengine.ext import db
from twig_db import Invitation
import random

import tools

def removeInvitation(code):
	"""
		verify and remove an invitation code from invitation pool
		return True on success, False otherwise
	"""
	q = db.GqlQuery( "SELECT * FROM Invitation "
				"WHERE code = :1 ", code )
	verified = (q.count() > 0)
	# a slight chance that multiple entities share the same code
	for e in q:
		e.delete()

	return verified

GEN_FORM = """
<form action="/invite/generate" method="get">
Generate codes<br /> Generate count:(1-10)
<input type="text" size="10" name="count">
<input type="submit" value="Generate">
</form>
"""

CLEAR_FORM = """
<form action="/invite/clear" method="get">
If you want to clear invitation code pool, use the button above<br />
note: there is NO CONFIRMATION for clearing invitation code!<br />
<input type="submit" value="Yes, I want to clear all invitation codes">
</form>
"""
class ManagementHandler(webapp2.RequestHandler):
	def get(self):
		q = db.GqlQuery( "SELECT * FROM Invitation " )
		
		self.response.write("<h1>Invitation code list</h1>")
		self.response.write( GEN_FORM )
		self.response.write("%d item(s) found" % q.count())
		self.response.write("<ul>")
		for e in q:
			self.response.write("<li>%s</li>" % e.code)
		self.response.write("</ul>")
		self.response.write(CLEAR_FORM)
		

class GenerateHandler(webapp2.RequestHandler):
	def get(self):
		"""
			generate invitation codes
		"""
		generate_count = self.request.get("count", default_value="0")
		try:
			generate_count = int( generate_count )
		except:
			self.response.write("bad argument")
			return

		if generate_count <= 0 or generate_count > 10:
			self.response.write("count out of range")
			return

		for x in range(generate_count):
			Invitation(code="%06d" % random.randint(0,999999)).put()
		self.redirect( '/invite/management' )

class ClearHandler(webapp2.RequestHandler):
	def get(self):
		"""
			clear all invitation codes
		"""
		q = db.GqlQuery ( "SELECT * FROM Invitation " )
		for e in q:
			e.delete()

		self.redirect( '/invite/management' )

app = webapp2.WSGIApplication(
		[
			(r'/invite/generate',		GenerateHandler),
			(r'/invite/clear',		ClearHandler),
			(r'/invite/management', 	ManagementHandler),
		], 
		debug=True)
