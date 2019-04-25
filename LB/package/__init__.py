from flask import Flask
from flask_cors import CORS
from threading import Timer
import time

app=Flask(__name__)
CORS(app)
app.config['SECRET_KEY']='5791628bb0b13ce0c676dfde280ba246'

from package import routes
