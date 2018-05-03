"""
Flask initialization
Server entry-point
comment
"""

from app.application import app

if __name__ == '__main__':
	app.run(debug = True)