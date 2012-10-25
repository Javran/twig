import webapp2
from google.appengine.api.app_identity import get_application_id
import tools
from version import VERSION

import twig_command
import twitter_command
import inspect
import category
import re
from reply import Reply
from cgi import escape

class CommandHelpHandler(webapp2.RequestHandler):
	def get(self):
		# grab a list of functions & methods
		valid_function = lambda f: \
				inspect.isfunction(f) and \
				f.__name__[:3] == 'cmd' and \
				f.__name__[3:] != ''
		func_list = inspect.getmembers( twig_command, valid_function )
		# transform func name to command
		func_list = map( lambda (name, f): (name[3:].lower(), f ), func_list )
		
		valid_method = lambda m: \
				inspect.ismethod(m) and \
				m.__name__[:6] == 'twiCmd' and \
				m.__name__[6:] != ''
		meth_list = inspect.getmembers( twitter_command.TwitterAPIWrapper, valid_method )
		# transform meth name to command
		meth_list = map( lambda (name, m): (name[6:].lower(), m ), meth_list )

		call_list = func_list + meth_list

		# arrange them by category
		func_dict = {}
		for key in category.category_description.keys():
			func_dict[key] = []
		for f in call_list:
			try:
				f_category = re.findall( r"# (\S+)", f[1].__doc__ )[0]
			except:
				f_category = "other"
			func_dict[f_category].append( f )
		
		func_tree = func_dict.items()	
		# sort category first
		func_tree = sorted( func_tree, key=lambda (c,_) : category.category_description[c][0] )
		# sort items inside 
		map( lambda (k, l): (k, sorted(l, key=lambda (name, f): name)) , func_tree )

		self.response.write("<h1>Command helps</h1>")
		
		# a dummy reply to keep cmdAlias work
		r = Reply()
		for k, ls in func_tree:
			if len(ls) == 0:
				continue
			# print category
			self.response.write("<b>%s</b><br />" % category.category_description[k][1])
			self.response.write("<ul>")
			for name, f in ls:
				# print func name and alias
				alias_list = sorted( twig_command.cmdAlias(None, name, r) )
				alias_list = map ( lambda n: '<font color="blue">%s</font>' % n, alias_list )
				self.response.write( "<li>%s</li>" % ' or '.join( alias_list ) )
	
				helps = re.findall( r"% (.*)$", f.__doc__, re.MULTILINE )
				self.response.write("<ul>")
				if len(helps) == 0:
					self.response.write("<li>no help for this command<li>")
				for line in helps:
					self.response.write("<li>%s</li>" % escape(line) )
				self.response.write("</ul>")

			self.response.write("</ul>")


app = webapp2.WSGIApplication(
		[
			(r'/help/commandhelp', CommandHelpHandler)
		], debug=True)
