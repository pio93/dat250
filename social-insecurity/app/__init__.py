from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import sqlite3
import os

# create and configure app
app = Flask(__name__)
Bootstrap(app)
csrf = CSRFProtect(app)
app.config.from_object(Config)

# TODO: Handle login management better, maybe with flask_login?
login = LoginManager()
login.init_app(app)
login.login_view = 'index'
db = SQLAlchemy(app)


from app import routes, models


  