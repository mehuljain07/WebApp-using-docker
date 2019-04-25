from flask import render_template, jsonify, request,url_for,redirect
from package import app,db
from package.models import User
from datetime import datetime
from flask_login import login_user, current_user, logout_user, login_required
from flask_cors import CORS,cross_origin
import hashlib
import requests

db.create_all()
reqCounter = 0
#Add a User
@app.route("/api/v1/users",methods = ['POST'])
def create_user():
	global reqCounter
	reqCounter = reqCounter + 1
	new_User = User.query.filter_by(username = request.get_json().keys()[0])
	if(new_User.first() is None):
		try:
			password = request.get_json()['password']
			if(len(password)<40):
				return str("Bad Request"),400
			password = hashlib.sha1(password).hexdigest()
			new_User = User(request.get_json()['username'],password)
			db.session.add(new_User)
			db.session.commit()
			return str('User Registered.</br>Please Go to <a href = login>Login page</a></br>'),201
		except Exception as e:
			return str(e),400
	else:
		return str("Username already taken"),400

#Signup
@app.route("/api/v1/signup",methods=['GET'])
def signup():
	return render_template("register.html"),200


#Login User
@app.route("/api/v1/login",methods = ['GET','POST'])
def loginUser():
	if(request.method == 'GET'):
		return render_template("login.html"),200
	else:
		result = request.form
		userName = result['username']
		password = result['password']
		user = User.query.filter_by(username = userName).first()
		if (user and (hashlib.sha1(password).hexdigest() == user.password)):
			login_user(user)
			return redirect("http://34.238.62.10:8000/api/v1/home"),201
		else:
			return str("Username/Password Incorrect."),400

#logout
@app.route("/api/v1/logout")
def logout():
	logout_user()
	return render_template('home.html'),400

#Remove a user
@app.route("/api/v1/users/<userName>",methods=['DELETE'])
def delete_user(userName):
	global reqCounter
	reqCounter = reqCounter + 1
	# if(current_user.is_authenticated):
	user = User.query.filter_by(username = userName)
	if(user.first() is None):
		return str("Users does not exist."),400
	else:
		stmt = "delete from User where username = '"+userName+"'"
		db.session.execute(stmt)
		db.session.commit()
		logout_user()
		return str("User "+userName+" deleted successfully"),200
	# else:
	#  	return render_template("login.html")

#List all users
@app.route("/api/v1/users",methods = ["GET"])
def get_all_users():
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		users = User.query.all()
		if(len(users) == 0):
			return str("No Content"),204
		response = []
		for user in users:
			response.append(user.username)
		return jsonify(response),200
	except Exception as e:
		return str("Bad Request"),405
		
#number of requests
@app.route("/api/v1/_count",methods=['GET','DELETE'])
def _count():
	global reqCounter
	if(request.method == "DELETE"):
		reqCounter = 0
		return jsonify([reqCounter]),200
	else:
		return jsonify([reqCounter]),200
