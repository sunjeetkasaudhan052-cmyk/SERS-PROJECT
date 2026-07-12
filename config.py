from flask_mysqldb import MySQL

mysql = MySQL()

class Config:
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "sunjeet@#ai123"
    MYSQL_DB = "sers"
    SECRET_KEY = "sers123"

def init_db(app):
    app.config.from_object(Config)
    mysql.init_app(app)