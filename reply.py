import twitter_object

class Reply(object):
	"""
		build reply
		
		first char in a line indicates its type
		A: list
		#: string
		=: assignment e.g: "= active_id: 123456" (tuple)
		!: warning string (put a leading '!' in str to distinguish from it)
		T: tweet
		>: extra information for the last message
		D: directmsg
		L: list
		R: raw data, in form : "R [len count], <raw>"

	"""
	
	def __init__(self):
		self.o = ""

	def r(self, obj):
		"""
			print raw object, which might contain strange characters
			output the len of the string first.
		"""
		txt = unicode( obj )
		self.o += "R %d, %s\n" % (len(txt), txt)

	def l(self, obj):
		"""
			append log
		"""
		if isinstance(obj, basestring):
			if obj[:1] == '!':
				self.o += "! %s\n" % obj[1:]
			else:
				self.o += "# %s\n" % obj
			return

		if isinstance(obj, tuple):
			self.o += "= %s: %s\n" % (obj[0], obj[1])
			return

		if isinstance(obj, list):
			if len(obj)>0:
				if isinstance(obj[0], twitter_object.Tweet):
					map(self.l, obj)
					return
				if isinstance(obj[0], twitter_object.DirectMessage):
					map(self.l, obj)
					return
				if isinstance(obj[0], twitter_object.ListInfo):
					map(self.l, obj)
					return

			self.o += "A [%s]\n" % ','.join( map(str, obj) )
			return
		
		if isinstance(obj, twitter_object.Tweet):
			self.o += "T %s, %s, %d\n" % (obj.owner, obj.id, len(obj.text))
			self.o += "> %s\n" % obj.text
			return
		
		if isinstance(obj, twitter_object.DirectMessage):
			self.o += "D %s, %s, %d\n" % (obj.sender, obj.id, len(obj.text))
			self.o += "> %s\n" % obj.text
			return
	
		if isinstance(obj, twitter_object.ListInfo):
			self.o += "L %s, %s, %s, %s, %s\n" % \
				( obj.id, obj.member, obj.subscriber, \
					len( obj.full_name ), len( obj.descrpition ) )
			self.o += "> %s\n" % obj.full_name
			self.o += "> %s\n" % obj.descrpition
			return

		self.o += "! unknown object, dump:\n" 
		self.r( obj )
