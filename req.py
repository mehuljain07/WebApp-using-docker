import requests
import time
import atexit
count=0

@atexit.register
def f():
	global count
	print("requests sent:"+str(count))

while(count<60):
	r=requests.get('http://34.238.62.10/api/v1/acts/count')
	time.sleep(3)
	print(count,r.status_code)
	#for resp in r.history:
	#print(r.history)
	count = count + 1

