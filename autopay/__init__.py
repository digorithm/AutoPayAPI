# Import flask and template operators
from flask import Flask
from flask.ext.httpauth import HTTPBasicAuth
# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy

auth = HTTPBasicAuth()

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)

# Build the database:
# This will create the database file using SQLAlchemy
#db.create_all()

from autopay.api import APIBase
