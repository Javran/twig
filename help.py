import webapp2
from google.appengine.api.app_identity import get_application_id
import tools
from version import VERSION
import markdown

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

		md_src = unicode()
		md_src += "# COMMAND HELPS\n\n"
		
		# a dummy reply to keep cmdAlias work
		r = Reply()
		for k, ls in func_tree:
			if len(ls) == 0:
				continue
			# print category
			md_src += "## %s\n" % category.category_description[k][1]
			for name, f in ls:
				# print func name and alias
				alias_list = sorted( twig_command.cmdAlias(None, name, r) )
				alias_list = map ( lambda n: '<font color="blue">%s</font>' % n, alias_list )
				md_src += "### %s\n" % ' or '.join( alias_list )
	
				helps = re.findall( r"% (.*)$", f.__doc__, re.MULTILINE )
				if len(helps) == 0:
					md_src += "#### no help for this command\n\n"
				for line in helps:
					md_src += "#### %s\n\n" % escape( line )

		tools.loadHead( self.response )
		self.response.write( markdown.markdown(md_src) )

import command

class BasicHelpHandler(webapp2.RequestHandler):
	def get(self):
		tools.loadHead( self.response )
		html = tools.parseMarkdown( "./page_src/basic.md", {
				"{{prefix}}" : command.PREFIX
			} )
		self.response.write( html )

app = webapp2.WSGIApplication(
		[
			(r'/help/commandhelp', 	CommandHelpHandler),
			(r'/help/basic',	BasicHelpHandler),
		], debug=True)
