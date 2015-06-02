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
		db.commit()

@app.cli.command('initdb')
def initdb_command():
	init_db()
	print('Initialized the database')

def get_db():
	if not hasattr(g 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/search')
def search():
	return show_results(request.form['query'])

#@app.route('/results/<query>')
def show_results(query):
	#retrieve account data from db
	cur = g.db.execute('select service, key from accounts order by id desc')
	accounts = [dict(service=row[0], key=row[1]) for row in cur.fetchall()]
	#get list of dictionaries by searching
	lst = []
	for (account in accounts):
		url = 'https://api.kloudless.com:443/v0/accounts/{0}/search/?q={1}'.format(account[key], query)
		lst.append([account.service, requests.get(url).contents])
	#change lst to list of dictionary with service = service, and results = string of results
	results = helper(lst)
	return render_template('show_results.html', results=results)

def helper(lst):
	d = []
	for piece in lst:
		s = ''
		for o in piece[1]['objects']:
			s = s + ',' + o
		d.append({'service' : piece[0], 'results' : s[1:]})
	return d

@app.route('/add/<service>/<int:key>', methods=['POST'])
def add_account():
	db = get_db()
	db.execute('insert into accounts (service, key) values (?, ?)', [service, key])
	g.db.commit()
	flash("Account added")
	return redirect(url_for('show_results'))

if __name__ == '__main__':
	app.run()