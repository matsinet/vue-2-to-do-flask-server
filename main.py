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
conn = sqlite3.connect('data/app.db')
c = conn.cursor()

# Setup Restful API Support
api = Api(app)

class Todo():
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    description = db.Column(db.Text)
    active = db.Column(db.Boolean)
    complete = db.Column(db.Boolean)

    def __init__(self, title, description, active, complete):
        self.title = title
        self.description = description
        self.active = active
        self.complete = complete

    def __repr__(self):
        return '{}'

    def findall():
        c.execute('SELECT * FROM todo');
        rows = c.fetchall()
        tasks = []
        for row in rows:
            tasks[] = Todo(row[])

class RequestResponse():
    success = True
    status = 200
    message = ''
    payload = []

    def __init__(self, message, payload, success = True, status = 200):
        self.success = success
        self.status = status
        self.message = message
        self.payload = payload

# TODO = {
#     'todo1': {'task': 'build an API'},
#     'todo2': {'task': '?????'},
#     'todo3': {'task': 'profit!'},
# }


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODO:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')

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
        
        response = RequestResponse()
        return rows
        
    def post(self):
        args = parser.parse_args()
        task_id = int(max(TODO.keys()).lstrip('todo')) + 1
        task_id = 'todo%i' % task_id
        TODO[task_id] = {'task': args['task']}
        return TODO[task_id], 201

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