import yaml
import sqlite3
import json
import os

from flask import Flask, g
from flask_restful import reqparse, abort, Api, Resource

config = yaml.safe_load(open('config/config.yaml'))

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Setup database
DATABASE = 'data/app.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def db_query(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def db_execute(query, args=()):
    cur = get_db().execute(query, args)
    get_db().commit()
    lastid = cur.lastrowid
    cur.close()
    return lastid


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Setup Restful API Support
api = Api(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

parser = reqparse.RequestParser()
parser.add_argument('id')
parser.add_argument('title')
parser.add_argument('description')
parser.add_argument('active')
parser.add_argument('complete')

# Todo
# shows a single todo item and lets you delete a todo item
class Task(Resource):
    def get(self, id):
        message = "record returned successfully"
        status = 200
        success = True
        row = db_query('SELECT * FROM todo WHERE id = ?', (id), one=True)
        if row is None:
            payload = []
            message = 'no matching record found'
            status = 404
            success = False
        else:
            payload = [dict(row)]
        response = {
            'success': success, 
            'status': status,
            'message': message,
            'payload': payload
        }
        return response

    def delete(self, id):
        query = 'DELETE FROM todo WHERE id = ?'
        id = db_execute(query, (id))
        message = 'task removed successfully'
        response = {
            'success': True, 
            'status': 200,
            'message': message,
            'payload': []
        }
        return response, 201

    def patch(self, id):
        args = parser.parse_args()
        title = args['title']
        description = args['description']
        active = args['active']
        complete = args['complete']
        valuestrings = []
        for key, value in args.items():
            if key != 'id':
                valuestrings.append('{0} = ?'.format(key))

        query = 'UPDATE todo SET {0} WHERE id = ?'.format(", ".join(valuestrings))
        rowid = db_execute(query, (title, description, active, complete, id))

        row = db_query('SELECT * FROM todo WHERE id = ?', [id], one=True)
        message = 'task updated successfully'
        response = {
            'success': True, 
            'status': 200,
            'message': ", ".join(valuestrings),
            'payload': [dict(row)]
        }
        return response, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TaskList(Resource):
    def get(self):
        todos = []
        rows = db_query('SELECT * FROM todo')
        for row in rows:
            todos.append(dict(row))
        message = "{} records returned successfully".format(len(todos))
        response = {
            'success': True, 
            'status': 200,
            'message': message,
            'payload': {'tasks': todos}
        }
        return response
        
        
    def post(self):
        args = parser.parse_args()
        title = args['title']
        description = args['description']
        query = 'INSERT INTO todo (%s) VALUES (%s)' % (
            ', '.join(('title', 'description')),
            ', '.join(['?'] * len((title, description)))
        )
        id = db_execute(query, (title, description))
        row = db_query('SELECT * FROM todo WHERE id = ?', [id], one=True)
        message = 'task created successfully'
        response = {
            'success': True, 
            'status': 200,
            'message': message,
            'payload': [dict(row)]
        }
        return response, 201


##
## Actually setup the Api resource routing here
##
api.add_resource(TaskList, '/tasks')
api.add_resource(Task, '/tasks/<id>')

@app.route('/')
def home():
    return "Please use a valid route", 404


if __name__ == '__main__':
    app.run(debug=True)