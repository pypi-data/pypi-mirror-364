pip install requests beautifulsoup4 sqlite3 pandas
import requests
import sqlite3
import schedule
import time
from bs4 import BeautifulSoup

_www_uri = 'false'
_www_db_sql = 'wwwpy_db_sqlite.db'

def set_task_uri(uri):
	_www_uri = str(uri)

def www_diver()
	url = uri
	response = requests.get(url)
	soup = BeautifulSoup(response.text, 'html.parser')
	quotes = soup.find_all('div', class_='quote')
	scraped_data = []
	for quote in quotes:
		text = quote.find('span', class_='text').text
		author = quote.find('small', class_='author').text
		scraped_data.append((text, author))
	for data in scraped_data:
		print(f"Quote: {data[0]}, Author: {data[1]}")
		sql_add(data)


def sql_setup(db_name)
	_www_db_sql = db_name
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, quote TEXT, author TEXT)''')
	# Commit and close the connection
	conn.commit()
	conn.close()

def sql_add(content):
	conn = sqlite3.connect(_www_db_sql)
	cursor = conn.cursor()
	cursor.executemany('''INSERT INTO quotes (quote, author) VALUES (?, ?)''', data)
	conn.commit()
	conn.close()

def set_task(uri, hour, minute):
	set_task_uri(uri)
	schedule.every().hour.at(check_schudell).do(www_diver)
	while True:
		schedule.run_pending()
		time.sleep(1)