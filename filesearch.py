import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import requests

import os

API_KEY = os.environ.get('API_KEY')

#configuration
DATABASE = '/tmp/filesearch.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

# @app.cli.command('initdb')
# def initdb_command():
# 	init_db()
# 	print('Initialized the database')

def get_db():
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def index():
	return render_template('show_results.html', appId=os.environ['APP_ID'])

@app.route('/search', methods=['POST'])
def search():
	return show_results(request.form['query'])

#@app.route('/results/<query>')
def show_results(query):
	#retrieve account data from db
	db = get_db()
	cur = db.execute('select service, key from accounts order by id desc')
	accounts = [dict(service=row[0], key=row[1]) for row in cur.fetchall()]

	account_string = ','.join([str(a['key']) for a in accounts])

	url = 'https://api.kloudless.com:443/v0/accounts/{0}/search/?q={1}'.format(account_string, query)

	resp = requests.get(url, headers={"Authorization": "ApiKey %s" % API_KEY})
	if resp.ok:
		dic = resp.json()

	#change lst to list of dictionary with service = service, and results = string of results
	results = [dict(name=a['name']) for a in dic['objects']]
	return render_template('show_results.html', appId=os.environ['APP_ID'], results=results)

@app.route('/add', methods=['POST'])
def add_account():
		db = get_db()
		db.execute('insert into accounts (service, key) values (?, ?)', [request.form['service'], request.form['key']])
		db.commit()
		return render_template('show_results.html', appId=os.environ['APP_ID'])

def main():
	for k in ['API_KEY', 'APP_ID']:
		if not os.environ.get(k):
			print('error')
			return

	init_db()
	app.run()

if __name__ == '__main__':
	main()