from datetime import datetime
from package import db
from flask import jsonify

class Category(db.Model):
	name = db.Column(db.String(200),nullable=False,unique=True,primary_key = True)
	acts = db.relationship('Act',backref = 'Category',lazy = True,cascade="all,delete-orphan")

	def __init__(self,name):
		self.name = name

	def serialize(self):
		return {'name':self.name}

class Act(db.Model):
	act_id = db.Column(db.Integer,primary_key = True)
	category = db.Column(db.String(200),db.ForeignKey('category.name'),nullable = False)
	caption = db.Column(db.String(200))
	imgFile = db.Column(db.String(200))
	username = db.Column(db.String(200),nullable = False)
	date_posted = db.Column(db.DateTime,default = datetime.utcnow)
	upvotes = db.Column(db.Integer,default = 0)

	def __init__(self,act_id,category,username,caption,imgFile,date_posted):
		self.act_id = act_id
		self.category = category
		self.caption=caption
		self.imgFile=imgFile
		self.username=username
		self.date_posted=date_posted
		self.upvotes = 0

	def serialize(self):
		return {'act_id' : self.act_id,'category':self.category,'caption':self.caption,'imgFile':self.imgFile,'username':self.username,'date_posted':self.date_posted,'upvotes':self.upvotes}
