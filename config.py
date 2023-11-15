# encoding:utf-8
import os
import pymysql

DEBUG = False

SECRET_KEY = os.urandom(24)

db = pymysql.connect(host='localhost', user='sqluser', password='password', db='OnlineForumPlatform', port=3306)

print(db)

