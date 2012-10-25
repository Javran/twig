import webapp2
import command
import twig_db
from reply import Reply

FORM = """
<h1>Command test</h1>
<form method="get" action="/test">
	<table>
		<tr>
			<td align="right">raw text:</td>
			<td align="left"><input type="text" name="raw" /></td>
		</tr>
		<tr>
			<td align="right">command:</td>
			<td align="left"><input type="text" name="cmd" /></td>
		</tr>
		<tr>
			<td align="right">params:</td>
			<td align="left"><input type="text" name="params" /></td>
		</tr>
		<tr>
			<td align="center" colspan="2"><input type="submit" value="test"></td>
		</tr>
	</table>
</form>
"""

class TestHandler(webapp2.RequestHandler):
	def get(self):
		raw = self.request.get("raw")
		cmd = self.request.get("cmd")
		params = self.request.get("params")
		if params is None:
			params = ''

		self.response.write(FORM)
		account = "aaa@gmail.com"
		r = Reply() 
		if raw is not None and len(raw)>0:
			# find active user of this account
			uid = twig_db.getActiveUser(account)

			isCmd, data = command.parseText( raw )	
			if isCmd:
				# is command
				cmd, params = data
				command.dispatchCommand(account, cmd, params, r)
			else:
				# is text
				if uid:
					command.dispatchCommand(account, 'send', data, r) 
				else:
					r.l("!no active account found")

		else:
			if cmd is not None and len(cmd)>0:
				command.dispatchCommand( account, cmd, params, r )
		
		reply = r.o
		if len(reply)>0:
			self.response.write( ("""
				<h1>Result</h1>
				value:<br /><textarea readonly="true" rows="20" cols="50">%s</textarea>
			""" % reply))

app = webapp2.WSGIApplication(
		[
			('/test',	TestHandler)
		], 
		debug=True)
