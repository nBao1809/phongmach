from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'KJHJF^(&*&&*OHH&*%&*TYUGJHG&(T&IUHKB'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/phongmachdb?charset=utf8mb4" % quote(
    'admin123')

db = SQLAlchemy(app=app)
login = LoginManager(app=app)

