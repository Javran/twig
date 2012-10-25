import webapp2
from google.appengine.api.app_identity import get_application_id
import tools
from version import VERSION

class MainHandler(webapp2.RequestHandler):
	def get(self):
		html = tools.parseMarkdown("index.md", {
			"{{app_name}}" : get_application_id(),
			"{{version}}": VERSION })
		self.response.write(html)

app = webapp2.WSGIApplication([(r'/.*', MainHandler)], debug=True)
