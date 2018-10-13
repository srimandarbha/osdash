from flask import Flask
from flask_bootstrap import Bootstrap
import datetime
import sys
import os

sys.path.append(os.getcwd() + '/scripts')

app = Flask(__name__)
Bootstrap(app)

from app import routes
