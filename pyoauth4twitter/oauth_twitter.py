# -*- coding: utf-8 -*-

import httplib
import urllib
import hmac
import hashlib
import binascii
import time
import urlparse
import random
import base64

percent_encode = lambda txt : urllib.quote(txt, '~')

class TwitterRequest(object):
	"""
		wrap twitter requests
		mainly used by 'TwitterConsumer._sign' process
	"""
	def __init__(self, method, url, content=''):
		"""
			method:		"POST" or "GET"
			url:		complete url
			content:	request contents(optional)

			* parameters both in content and url are given precent encoded.
			* but here I'd better decode them and store them in a dict
		"""
		self.method = method
		self.content = content
		result = urlparse.urlsplit( url )
		# parse base_url 
		#	e.g.: "https://xxxx/xxx/x" and 
		#	url(query included) 
		#	e.g.:"/xxx/x?a=1"
		self.base_url = "%s://%s%s" % (result.scheme, result.netloc, result.path)
		self.url = result.path	
		if result.query != '':
			self.url += '?' + result.query
		# break params into dict
		self.params = urlparse.parse_qs ( result.query )
		# parse content as well ...
		# note: result of urlparse.parse_qs seems decoded...
		self.params.update( urlparse.parse_qs( content ) )
		# iron value assuming there is only one possible value in value list
		self.params = dict( (k,v[0]) for k, v in self.params.iteritems() )
		
	def get_response(self, connection , header):
		"""
			connection:	a HTTPConnection object to use
			header:		extra request headers

			* this function is used indirectly for coding convenience,
			  generally 'connection' is provided 
			  by a 'TwitterConsumer' object
		"""
		connection.request(self.method, self.url, self.content, header)
		response = connection.getresponse()
		# assert response.status == 200
		return response

class TwitterConsumer(object):
	"""
		OAuth abstract twitter consumer
	
		* a demo of obtaining access token
		  ref: https://dev.twitter.com/docs/auth/implementing-sign-twitter

		* a demo of authorizing twitter requests with oauth
		  ref: https://dev.twitter.com/docs/auth/creating-signature
		  ref: https://dev.twitter.com/docs/auth/authorizing-request

	"""
	def __init__(self, key, secret, callback='', verbose=False):
		"""
			key:		consumer key
			secret:		consumer secret
			callback:	callback url, e.g.:http://localhost/callback/

			* you can leave callback blank if you don't request access token
		"""
		self.key = key
		self.secret = secret
		self.callback = callback
		self.token = ''
		self.token_secret = ''
		self.a_token = ''
		self.a_secret = ''
		self.verbose = verbose

		self.connection = httplib.HTTPSConnection('api.twitter.com')

	def for_user(self, a_token, a_secret):
		"""
			prepare for user request authorizing
			a_token:	oauth access token
			a_secret:	oauth access token secret

		"""
		self.a_token = a_token
		self.a_secret = a_secret

	def has_user(self):
		"""
			has this instance bound with a user token?
		"""
		return len( self.a_token ) > 0 and len( self.a_secret ) > 0

	def request_token(self):
		"""
			Step #1: request_token	
		"""
		response = self.get_response(
			TwitterRequest( 
				"POST", 
				"https://api.twitter.com/oauth/request_token"))

		data = response.read()
		result = urlparse.parse_qs( data )
		self.token = result["oauth_token"][0]
		self.token_secret = result["oauth_token_secret"][0]
		
		self._print ("Token is: " + self.token)
		self._print ("Token secret is:" + self.token_secret)
		
	def authenticate(self):
		"""
			Step #2: authenticate	
		"""
		print "Please goto: https://api.twitter.com/oauth/authenticate?oauth_token=%s" % self.token
		data = raw_input( "Tell me redirected url address:\n" )
		result = urlparse.urlparse( data )
		r_callback = "%s://%s%s" % (result.scheme, result.netloc, result.path)
	
		assert r_callback == self.callback
		self._print ("Callback check ok.")
		
		result = urlparse.parse_qs( result.query )
		r_token = result["oauth_token"][0]	
		assert r_token == self.token
		self._print ("Token check ok.")
		
		self.verifier = result["oauth_verifier"][0]
		self._print ("Verifier is: " + self.verifier)

	def access_token(self):
		"""
			Step #3: access_token
		"""
		response = self.get_response(
			TwitterRequest( 
				"POST", 
				"https://api.twitter.com/oauth/access_token?oauth_verifier=%s" % self.verifier))

		data = response.read()
		result = urlparse.parse_qs( data )
		#raise NameError(data)
		self.user_id = result["user_id"][0]
		self.screen_name = result["screen_name"][0]
		self.a_token = result["oauth_token"][0]
		self.a_secret = result["oauth_token_secret"][0]

		self._print ("Welcome %s, your user_id is: %s" % (self.screen_name, self.user_id) )
		self._print ("Access token is: " + self.a_token )
		self._print ("Access secret: " + self.a_secret )

	def get_response(self, twitter_request):
		"""
			authorize a TwitterRequest, send it, and get response
		"""
		payload = self._oauth_payload_generate()
		header = self._sign(oauth_payload = payload, request = twitter_request)
		return twitter_request.get_response( self.connection, header )

	def _sign(self, oauth_payload, request):
		"""
			make header field - Authorization
		"""
		# merge params
		# use oauth_payload to update request params might avoid 
		# some oauth params's accidental overriding
		payload = dict( request.params )
		payload.update( oauth_payload )

		# here I assume that all keys contain only 'a-zA-Z_.-'
		# thus there is no necessity to percent-encode them
		# will now sort them according to their original value

		keylist = sorted( payload.keys() )
		rawlist = []
		for k in keylist:
			encoded_value = percent_encode( payload[k] )
			rawlist.append( "%s=%s" % (k, encoded_value) )

		# craft base string
		base_string = request.method.upper()
		base_string += '&'
		base_string += percent_encode(request.base_url)
		base_string += '&'
		base_string += percent_encode( '&'.join( rawlist ) )

		# craft signing key
		if self.has_user():
			signing_key = "%s&%s" % ( percent_encode(self.secret), percent_encode(self.a_secret) )
		else:
			signing_key = "%s&%s" % ( percent_encode(self.secret), percent_encode(self.token_secret) )

		# sign base_string
		hashed = hmac.new(signing_key, base_string, hashlib.sha1)
		signature = binascii.b2a_base64(hashed.digest())[:-1]
		
		# append signature field
		oauth_payload["oauth_signature"] = signature

		# prepare relevant oauth values
		oauth_entry = []
		for k in oauth_payload.keys():
			encoded_value = percent_encode( oauth_payload[k] )
			oauth_entry.append( '%s="%s"' % (k, encoded_value) )

		oauth_str = 'OAuth ' + ','.join(oauth_entry)
		# field crafted
		return { "Authorization" : oauth_str }

	def _oauth_nonce_generate(self):
		"""
			generate a nonce
			* any approach which produces 
			  a relatively random alphanumeric string should be OK.
		"""
		raw_data = random.getrandbits(32 * 8)
		raw_str = ''
		for i in range(32):
			new_part = raw_data % 256
			raw_data /= 256
			raw_str += chr(new_part)
	
		encoded = base64.b64encode(raw_str) 
		return encoded.rstrip('=').replace('+', 'A').replace('/', 'B')

	def _oauth_payload_generate(self):
		"""
			generate payload that required by OAuth
		"""
		result = {
			"oauth_consumer_key" : self.key,
			"oauth_nonce" : self._oauth_nonce_generate(),
			"oauth_signature_method" : "HMAC-SHA1",
			"oauth_timestamp" : str( int( time.time()) ),
			"oauth_version" : "1.0"
		}

		# * if token is unavaliable, this func must be called from request_token
		#   provide callback addr instead.
		# * access token should have a higher priority ...
		if self.has_user():
			result["oauth_token"] = self.a_token
		else:
			if len( self.token ) > 0:
				result["oauth_token"] = self.token
			else:
				result["oauth_callback"] = self.callback

		return result

	def _print(self, text):
		"""
			print things if I'm verbose
		"""
		if self.verbose:
			print text
