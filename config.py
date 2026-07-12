import os
from flask_mysqldb import MySQL

mysql = MySQL()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "sers")
    SECRET_KEY = os.getenv("SECRET_KEY", "sers123")

def init_db(app):
    app.config.from_object(Config)
    mysql.init_app(app)