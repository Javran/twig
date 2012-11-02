

class Tweet(object):
	def __init__(self, data):
		self.data = data
		self.id = data["id_str"]
		self.text = data["text"]
		self.owner = data["user"]["screen_name"]

class DirectMessage(object):
	def __init__(self, data):
		self.data = data
		self.id = data["id_str"]
		self.sender = data["sender_screen_name"]
		self.text = data["text"]

class ListInfo(object):
	def __init__(self, data):
		self.data = data
		self.id = data["id_str"]
		self.full_name = data["full_name"]
		self.descrpition = data["description"]
		self.member = data["member_count"]
		self.subscriber = data["subscriber_count"]

class Status(object):
	def __init__(self, data):
		self.data = data
		self.name = data["name"]
		self.location = data["location"]
		self.description = data["description"]
		self.screen_name = data["screen_name"]
		self.id = data["id"]
		self.statuses_count = data["statuses_count"]
		self.friends_count = data["friends_count"]
		self.followers_count = data["followers_count"]
		try:
			data["status"]["user"] = { "screen_name" : self.screen_name }
			self.status = Tweet(data["status"])
		except:
			self.status = None
