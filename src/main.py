from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

import yaml

config = yaml.safe_load(open('config/config.yaml'))

app = Flask(__name__)
api = Api(app)

TASKS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TASKS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Task(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TASKS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TASKS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TASKS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TaskList(Resource):
    def get(self):
        return TASKS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TASKS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TASKS[todo_id] = {'task': args['task']}
        return TASKS[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TaskList, '/tasks')
api.add_resource(Task, '/tasks/<todo_id>')


if __name__ == '__main__':
    app.run(debug=True)