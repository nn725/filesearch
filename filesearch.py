import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import requests

#configuration
DATABASE = '/tmp/filesearch.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object('keys', silent=True)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit

@app.route('/search')
def search():
	return requests.get('https://api.kloudless.com:443/v0/accounts/70205824/search/?q=h').content;


if __name__ == '__main__':
	app.run()