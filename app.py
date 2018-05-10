import os # Incase we need to mess with Heroku Dyno binaries/packages.

from flask import Flask, make_response, jsonify, Response, render_template
from flask_restful import reqparse, Resource
from flask_cors import CORS, cross_origin

from database import Database
from database import CursorFromConnectionFromPool
from urllib.parse import urlparse # To parse Heroku DB URL.
import psycopg2

import xml.etree.cElementTree as ET

app = Flask(__name__)
CORS(app)

url = urlparse('postgres://ucyroaeunxxsrn:e042657f9582726c420bf5bc72987796f029d915b78a756b3fa93c0d8603276c@ec2-174-129-225-9.compute-1.amazonaws.com:5432/d8rdejefc72ive')
Database.initialize(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, sslmode='require')

''' GET '''
@app.route('/api/v1/getLocations', methods=['GET'])
def hello_world():
	with CursorFromConnectionFromPool() as cursor:
		try:
			sql_string = 'SELECT * from locations'
			cursor.execute(sql_string)
			result = cursor.fetchall()

			root = ET.Element("markers")

			for res in result:
				marker = ET.SubElement(root, "marker", id="Array", lat='{}'.format(res[1]), lng='{}'.format(res[2]), 
					phone='{}'.format(res[3]), severity='{}'.format(res[4]))

			tree = ET.ElementTree(root)			
			
			tree.write('templates/file.xml')
			data = ET.dump(root)
			return render_template('file.xml'), 201, {'Content-Type': 'text/xml'}
		except psycopg2.IntegrityError:
			result = {'message' : 'Resources not found.', 'status' : 404}
			jsonify(result)


''' POST '''
@app.route('/api/v1/postLocation', methods=['POST'])
def postLocation():
	parser = reqparse.RequestParser(bundle_errors=True)
	parser.add_argument('lat', required=True, help="You need latitude.")
	parser.add_argument('lng', required=True, help="You need longitude.")
	parser.add_argument('phone', required=True, help="You need a phone number.")
	parser.add_argument('severity', required=True, help="You need severity.")

	args = parser.parse_args()

	response = None
	with CursorFromConnectionFromPool() as cursor:
		try:
			sql_string = 'INSERT INTO locations (lat, lng, phone, severity) VALUES (%s, %s, %s, %s) RETURNING id, lat, lng, phone, severity'
			cursor.execute(sql_string, (args['lat'], args['lng'], args['phone'], args['severity']))
			id_of_new_row = cursor.fetchone()
			response = {
				'message:' : 'location created successfully',
				'status' : 201,
				'id' : id_of_new_row[0],
				'lat' : id_of_new_row[1],
				'lng' : id_of_new_row[2],
				'phone' : id_of_new_row[3],
				'severity' : id_of_new_row[4]
			}
			return jsonify(response)
		except psycopg2.IntegrityError:
			# We already have an entry with the same email address (return HTTP code 409 - conflict).
			response = {'message:' :'Duplicate Location' , 'status' : 409}
			return jsonify(response)

	

if __name__ == "__main__":
	app.run(port=5000, debug=True)