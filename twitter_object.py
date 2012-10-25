

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
