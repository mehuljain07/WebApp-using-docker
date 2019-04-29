from flask import render_template,jsonify,request,redirect
from package import app
from flask_cors import CORS,cross_origin
import requests
import docker
import time
import threading
import atexit
import json
reqCounter=0
container_count=0
port_dict={}
def conStop(id):
	try:
		global container_count
		global port_dict
		container_count=container_count-1
		port=list(port_dict.keys())[list(port_dict.values()).index(id)]
		port_dict.pop(port)
		client=docker.from_env()
		container=client.containers.get(id)
		container.stop()
		container.remove()
		time.sleep(1)
	except Exception as e:
		print(e)

def conStart(port):
	try:
		global container_count
		global port_dict
		client=docker.from_env()
		container=client.containers.create('acts:latest',ports={'80/tcp':str(port)},detach=True,tty=True,stdin_open=True,volumes={'newvolume':{'bind':'/app','mode':'rw'}})
		container.start()
		time.sleep(0.5)
		port_dict[port]=container.id
		container_count=container_count+1
	except Exception as e:
		print(e)

def poll():
	global port_dict
	client=docker.from_env()
	#print("inside poll()")
	while True:
		for port in port_dict.keys():
			try:
				url = 'http://127.0.0.1:'+str(port)+'/api/v1/_health'
				time.sleep(0.01)
				r = requests.get(url)
				print(r.status_code)
				if(r.status_code == 500):
					conStop(port_dict[port])
					conStart(port)
			except Exception as e:
				print(e)
		time.sleep(1)

def scale():
	while True:
		global reqCounter
		global port_dict
		count1=reqCounter
		#print(count1)
		time.sleep(120)
		count2=reqCounter
		#print(count2)
		if(count2-count1+1<20):
			if(container_count>1):
				while(container_count>1):
					conStop(port_dict[port_dict.keys()[-1]])
		if(count2-count1+1 >=20 and count2-count1+1<40):
			ports = port_dict.keys()
			if(container_count==1):
				conStart(sorted(ports)[-1]+1)
			elif(container_count>2):
				while(container_count>2):
					conStop(port_dict[ports[-1]])
		elif(count2-count1+1>=40 and count2-count1+1<60):
			if(container_count < 3):
				while(container_count!=3):
					conStart((sorted(port_dict.keys()))[-1]+1)
			elif(container_count > 3):
				while(container_count>3):
					conStop(port_dict[port_dict.keys()[-1]])
@app.before_first_request
def initialize():
	if(container_count < 1):
		conStart(8000)

@app.route('/', defaults={'path':''})
def emptyRequest(path):
	return str("Path not found"),404

@app.route('/api/v1/<path:path>',methods=['GET','POST','DELETE'])
def catch_all(path):
	global reqCounter
	global container_count
	reqCounter=reqCounter+1
	if(reqCounter==1):
		t1=threading.Thread(target=poll,name='polls')
		t2=threading.Thread(target=scale,name='scaleing')
		t1.daemon=True
		t2.daemon=True
		t1.start()
		t2.start()

	port_i = (reqCounter % container_count)
	port=port_dict.keys()[port_i]
	#print(port)
	url = 'http://127.0.0.1:'+str(port)+'/api/v1/'+path
	header = {'Origin':'34.238.62.10'}
	try:
		if(request.method=='GET'):
			time.sleep(0.01)
			r = requests.get(url,allow_redirects=True,headers=header)
			return r.content,r.status_code
		elif(request.method == 'POST'):
			time.sleep(0.01)
			r = requests.post(url,json=request.get_json(),headers=header)
			return r.content,r.status_code
		elif(request.method == 'DELETE'):
			time.sleep(0.01)
			r = requests.delete(url,headers=header,allow_redirects=True)
			return r.content,r.status_code
	except Exception as e:
		print(e)

@atexit.register
def close_all():
	global port_dict
	for port in port_dict.keys():
		conStop(port_dict[port])
	print("All Containers Closed! Exiting Normally")
