from google.appengine.ext import db

def getUser(uid):
	"""
		find the user entity given uid
	"""
	query = db.GqlQuery( "SELECT * FROM User "
				"WHERE uid = :1", uid)
	return query.get()

def getAccount(account):
	"""
		find the account entity given account name
	"""
	query = db.GqlQuery( "SELECT * FROM Account "
				"WHERE account = :1 ", account)
	return query.get() 

def getActiveUser(account):
	"""
		find the active user of a given account
	"""
	acc = getAccount(account) 
	if acc is None:
		return None

	return acc.active_id

def getUserInfo(account):
	"""
		get the (a_token, a_secret, uid) tuple for a given account
	"""
	# find active user first
	uid = getActiveUser(account)
	if uid is None:
		return None
	
	# get pair
	query = db.GqlQuery( "SELECT * FROM User "
				"WHERE uid = :1 ", uid)
	e = query.get()
	return (e.a_token, e.a_secret, uid)

class OAuthRequest(db.Model):
	"""
		temporarily store request tokens required for obtaining access token
		* when access token is obtained, relevant data should be removed
	"""
	# request token
	token = db.StringProperty(required=True)
	token_secret = db.StringProperty()

	# user data
	user_id = db.StringProperty()
	access_token = db.StringProperty()
	access_secret = db.StringProperty()

	# use this code to obtain access token pair via gtalk 
	code = db.StringProperty()
	
	# entry create time
	created = db.DateTimeProperty(auto_now_add=True)

# the tables below are used for verified users

class User(db.Model):
	"""
		store access token & access token secret for users
	"""
	# all fields are required
	uid = db.StringProperty(required=True)
	a_token = db.StringProperty(required=True)
	a_secret = db.StringProperty(required=True)

class Account(db.Model):
	"""
		account here means gtalk/XMPP accounts
	"""
	# each entity bind a specific user_id with account
	# to make it possible for multi-user switch
	account = db.StringProperty(required=True)
	active_id = db.StringProperty()

class RelationAccountUser(db.Model):
	"""
		relationship between account and user
	"""
	account = db.ReferenceProperty(Account)
	user = db.ReferenceProperty(User)

class Invitation(db.Model):
	"""
		invitation code pool
	"""
	code = db.StringProperty(required=True)
