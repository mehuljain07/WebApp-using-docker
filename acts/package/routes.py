from flask import render_template, jsonify, request,redirect
from package import app,db
from package.models import Category,Act
from datetime import datetime
import pybase64
import ast
from sqlalchemy import update,exc
from flask_cors import CORS,cross_origin
import binascii
import requests

db.create_all()

crash=0
reqCounter=0

#home
@app.route("/api/v1/home")
def go_home():
	global crash
	if(crash == 1):
		return str(""),500
	try:
		return render_template("home.html",cats = Category.query.all()),200
	except Exception as e:
		return str(e),400

#Add a Category
@app.route('/api/v1/categories', methods=['POST'])
def add_categories():
	global crash
	if(crash == 1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		reader = request.get_json()[0]
		#reader = request.stream.read()
		if(len(reader) == 0):
			return str("bad request"),400
		#return str("hi"+reader[0]),201
		#reader = ast.literal_eval(reader)
		#return str(reader),201
		newCat = Category(reader)
		db.session.add(newCat)
		db.session.commit()
		return str("Category Added Successfully"),201
	except exc.IntegrityError as e:
		return str("Integrity Error"),400

#List All Categories
@app.route('/api/v1/categories', methods=['GET'])
def get_categories():
	global crash
	if(crash == 1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		categories = Category.query.all()
		response = {}
		if(len(categories) == 0):
			return str("No Content"),204
	 	#return categories
		for cat in categories:
			response[cat.name] = len(cat.acts)
		return jsonify(response),200
	except Exception as e:
		return str(e),400

# Remove a Category
@app.route('/api/v1/categories/<categoryName>',methods=['DELETE'] )
def delete_cat(categoryName):
	global crash
	if(crash== 1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		cat = Category.query.filter_by(name = categoryName)
		if(cat.first() is None):
	 		return str("Bad Request! Category does not exist."),400
		else:
		 	stmt = "delete from Category where name = '"+categoryName+"'"
		 	db.session.execute(stmt)
		 	db.session.commit()
		 	return str("Category "+categoryName+" deleted successfully"),200
	except Exception as e:
		return str(e),400

#List All Acts for a given Category.
@app.route('/api/v1/categories/<categoryName>/acts',methods = ['GET'])
def listActs(categoryName):
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	r = request.args
	if(len(r)==0):
		try:
			cat = Category.query.filter_by(name = categoryName)
			if(cat.first() is None):
				return str("Category Not Found!"),204
			else:
				acts = cat.first().acts
				response=[]
				if(len(acts) < 100 and len(acts)>0):
					for act in acts:
						response.append(act.serialize())			
					return jsonify(response),200
				elif(len(acts)>=100):
					return str("Payload Too Large"),413
				else:
					return jsonify('No Content'),204
		except Exception as e:
			return str(e),400
	else:
		cat = Category.query.filter_by(name = categoryName).first()
		if(cat is None):
			return str("Bad Request"),400
		allAct = cat.acts
		startRange = int(r.get('start'))
		endRange = int(r.get('end'))
		if(startRange>=1 and startRange <len(allAct) and endRange >= startRange):
			if(endRange <=len(allAct)):
				requiredActs = allAct[startRange-1:endRange-1]
			else:
				requiredActs = allAct[startRange-1:]
			requiredActs.sort(key = lambda x : x.date_posted,reverse = True)
			if(len(requiredActs) <=100 and len(requiredActs)>0):
				response = []
				for act in requiredActs:
					response.append(act.serialize())
				return jsonify(response),200
			elif(len(requiredActs) == 0):
				return str("No Content"),204
			else:
				return str("Payload too large"),413
		else:
			return str("Bad Request"),400

#Add an act
@app.route('/api/v1/addacts',methods=['GET'])
def addnact():
	global crash
	if(crash==1):
		return str(""),500
	if(request.method == 'GET'):
		return render_template('upload.html')

#Add an Act
@app.route('/api/v1/acts',methods = ['POST'])
def addAct():
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		result = request.get_json()
		#return str(type(result)),200
		if('upvotes' in result.keys()):
			return str("Bad Request"),400
		cat = Category.query.filter_by(name = result['categoryName']).first()
		header = {'Origin':'3.210.29.181'}
		r = requests.get('http://34.238.62.10/api/v1/users',headers = header)
		if(r.status_code == 405):
			return str(r.text),405
		elif(r.status_code == 204):
			return str("Bad Request"),400
		else:
			users = ast.literal_eval(r.text)
		user = result['username']
		if(user not in users or cat is None):
			return str("Bad Request"),400
		if('timestamp' in result.keys()):
			date = datetime.strptime(result['timestamp'],'%d-%m-%Y:%S-%M-%H')
		else:
			now=datetime.now()
			date = now.strftime('%d-%m-%Y:%S-%M-%H')
			date = datetime.strptime(date,'%d-%m-%Y:%S-%M-%H')
		#return str(type(result['imgB64'])),201
		imgFile = pybase64.b64decode(result['imgB64'].rstrip(),validate = True)
		new_act = Act(act_id = result['actId'],category = cat.name, username = user,caption = result['caption'],imgFile = result['imgB64'],date_posted = date)
		db.session.add(new_act)
		db.session.commit()
		return str("Act Added successfully"),201
	except exc.IntegrityError as e1:
		return str("Integrity Error"),400
	except binascii.Error as e2:
		return str(e2),400
	except Exception as e2:
		return str(e2),400

#Return number of acts in a category
@app.route('/api/v1/categories/<categoryName>/acts/size',methods = ['GET'])
def get_size(categoryName):
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		cat = Category.query.filter_by(name = categoryName).first()
		if(cat is None):
			return str("Bad Request"),400
		else:
			if(len(cat.acts) > 0):
				return jsonify([len(cat.acts)]),200
			else:
				return str("No Content"),204
	except Exception as e:
		return str(e),400


#upvote an act
@app.route('/api/v1/acts/upvote',methods = ['POST'])
def upvote():
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		reader = request.stream.read()
		if (len(reader)==0):
			return str("Bad Request"),400
		r = ast.literal_eval(reader)
		if(isinstance(r,(int,long))):
			actId = r
		else:
			actId = r[0]
		act = Act.query.filter_by(act_id = actId).first()
		if(act is None):
			return str("Act Does not exists!"),400
		else:
			upvote = act.upvotes
			Act.query.filter_by(act_id = actId).update({'upvotes': upvote+1})
			db.session.commit()
			return str("upvote Successful"),200
	except Exception as e:
		return str(e),400

#Remove an Act
@app.route('/api/v1/acts/<actId>',methods = ['DELETE'])
def del_act(actId):
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	try:
		act = Act.query.filter_by(act_id = actId).first()
		if(act is None):
			return str("Act Id is Invalid"),400
		else:
			stmt = "delete from Act where act_id = '"+actId+"'"
			db.session.execute(stmt)
			db.session.commit()
			return str("Act removed successfully"),200
	except Exception as e:
		return str(e),400

#Display acts of a category
@app.route('/api/v1/categories/<categoryName>/acts/display' , methods = ['GET'])
def disp(categoryName):
	global crash
	if(crash==1):
		return str(""),500
	try:
		cat = Category.query.filter_by(name = categoryName)
		acts = cat.first().acts
		if(len(acts) < 100):
			return render_template("acts.html",cat = categoryName, acts = acts),201
		else:
			return render_template("acts.html",cat = categoryName,acts = []),201
	except Exception as e:
		return str(e),400

#return number of acts
@app.route('/api/v1/acts/count',methods=['GET'])
def actsCount():
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	reqCounter = reqCounter + 1
	acts = Act.query.all()
	return jsonify([len(acts)]),200

#return count of requests
@app.route('/api/v1/_count',methods=['GET'])
def _count():
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	if(request.method == 'GET'):
		return jsonify([reqCounter]),200

#reset counter
@app.route('/api/v1/_count',methods=['DELETE'])
def resetCount():
	global crash
	if(crash==1):
		return str(""),500
	global reqCounter
	reqCounter = 0
	return jsonify([reqCounter]),200

#Health Check
@app.route('/api/v1/_health',methods=['GET'])
def health_check():
	global crash
	if (crash==1):
		return str(" "),500
	try:
		newCat = Category("testCategory")
		db.session.add(newCat)
		#db.session.commit()
		categories=Category.query.all()
		db.session.delete(newCat)
		db.session.commit()
		return str("DB connection working "),200
	except Exception as e:
		return str(e),500

#crash api
@app.route('/api/v1/_crash',methods=['POST'])
def crash():
	global crash
	crash = 1
	return str("App Crashed!"),200
