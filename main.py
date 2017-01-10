import os
import yaml
import sqlite3
import json

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


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODO:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('id')
parser.add_argument('title')
parser.add_argument('description')
parser.add_argument('active')
parser.add_argument('complete')

# Todo
# shows a single todo item and lets you delete a todo item
class Task(Resource):
    def get(self, task_id):
        abort_if_todo_doesnt_exist(task_id)
        return TODO[task_id]

    def delete(self, task_id):
        abort_if_todo_doesnt_exist(task_id)
        del TODO[task_id]
        return '', 204

    def put(self, task_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODO[task_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TaskList(Resource):
    def get(self):
        todos = []
        rows = db_query('select * from todo')
        for row in rows:
            todos.append(dict(row))
        message = "{} records returned".format(len(todos))
        response = {
            'success': True, 
            'status': 200,
            'message': message,
            'payload': todos
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
api.add_resource(Task, '/tasks/<task_id>')

@app.route('/')
def home():
    return "Please use a valid route"


if __name__ == '__main__':
    app.run(debug=True)