import os # Incase we need to mess with Heroku Dyno binaries/packages.

from flask import Flask

from database import Database
from urllib.parse import urlparse # To parse Heroku DB URL.

app = Flask(__name__)

@app.route('/api/v1/getLocations')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
	app.run(port=5000, debug=True)