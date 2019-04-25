from datetime import datetime
from package import db,login_manager
from flask import jsonify
from flask_login import UserMixin

@login_manager.user_loader
def load_user(username):
	return User.query.get(username)

class User(db.Model,UserMixin):
	username = db.Column(db.String(200),primary_key = True)
	password = db.Column(db.String(200))
	
	def __init__(self,username,password):
		self.username = username
		self.password = password

	def get_id(self):
		return self.username

	def serialize(self):
		return {'username' : self.userame,'password':self.password}