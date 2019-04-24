import logging
import sqlite3
from flask import Flask
from flask import jsonify
from flask import render_template
from flask_restful import request
from flask_restful import Resource, Api
from module import dict_factory, create_table, create_todo, get_all, validate_todo, search_todo, \
    delete_status, delete_due_date, delete_all, delete_by_transaction_id, update_todo

# Logger for errors and http requests
logging.basicConfig(filename='error.log',level=logging.ERROR)


# Sqlite3 database storage
# Singleton object which restrict further connections
DATABASE= "todo.db"
conn = sqlite3.connect(DATABASE, check_same_thread=False)
conn.row_factory = dict_factory
cur = conn.cursor()
cursor = conn.cursor()

# Creating table only if no table exist
create_table(conn)

app = Flask(__name__)
api = Api(app)


def basic_validations(args, check_status=True):
    """Basic validations for arguments"""

    for k, v in args.items():
        if not k:
            if not isinstance(v, str):
                error = 'Argument parameter should only be a string'
                return error

        if k not in ['status', 'task', 'due_date']:
            error = 'Invalid Argument parameter'
            logging.error(error)
            return error

        status = args.get('status')
        task = args.get('task')
        due_date = args.get('due_date', "")

        error = validate_todo(status, task, due_date, check_status)
        if error:
            return error

        return


class Status(Resource):
    """ Get status of Webserver """
    def get(self):
        response = {'status': 'Active'}
        return jsonify(response)


class TODO(Resource):
    """ API for TODO Tasks """

    def get(self):
        """Overriding get method for retrieving"""
        args = request.args.copy()

        # Check for app;y validation check on status
        check_status = False
        status = args.get('status')
        task = args.get('task')
        due_date = args.get('due_date', "")
        if not status:
            args['status'] = ""
        else:
            status = status.lower().replace('~', "").replace("_", " ")
            args['status'] = status
            check_status = True

        if not task:
            args['task'] = ""
        else:
            task = task.replace("~", "")
            args['task'] = task

        error = basic_validations(args, check_status)
        if error:
            return {"error":error}, 400

        # Check if its any specific filter
        if any([status, task, due_date]):
            resp = search_todo(cursor, status, task, due_date)
        else:
            resp = get_all(cursor)

        return jsonify(resp)

    def post(self):
        """Overriding get method for creating todo task"""
        data = request.form.copy()
        status = data.get('status', "")
        task = data.get('task')
        due_date = data.get('due_date', "")
        if status:
            status = status.lower()
            data['status'] = status

        error = basic_validations(data)
        if error:
            return {"error":error}, 400

        error = create_todo(conn, status, task, due_date)
        if error:
            return {"error":error}, 500

        return {}, 201

    def delete(self):
        """Overriding get method for delete todo task"""
        data = request.form.copy()
        status = data.get('status', "")
        task = data.get('task')
        due_date = data.get('due_date', "")
        transaction_ids = data.get("transaction_id")

        # Delete by transaction ID(s)
        if transaction_ids:
            ids = transaction_ids.split(",")
            error = delete_by_transaction_id(conn, ids)
            if error:
                return {'error': error}, 400

            return {}, 410

        # Delete all if no argument provided
        if not any([status, due_date]):
            error = delete_all(conn)
            if error:
                return {'error': error}, 400

        if status:
            status = status.lower()
            data['status'] = status
        else:
            data['status'] = ""

        if not task:
            data['task'] = ""

        error = basic_validations(data, check_status=False)
        if error:
            return {'error': error}, 400

        # Delete by status
        if status:
            error = delete_status(conn, status)
            if error:
                return {'error': error}, 500

        # Delete by due_date
        elif due_date:
            error = delete_due_date(conn, due_date)
            if error:
                return {'error': error}, 500


        return {}, 410


    def put(self):
        """Overriding get method for update todo task"""
        check_status = True
        data = request.form.copy()
        status = data.get('status', "")
        task = data.get('task')
        due_date = data.get('due_date', "")
        transaction_ids = data.get("transaction_id")

        # Transaction ID is must to update any todo task
        if not transaction_ids:
            error = "Transaction ID not provided"
            return {'error': error}, 400

        # If there is no data to update return
        if not any([status, task, due_date]):
            error = "No valid parameter(s) are provided to update"
            return {'error': error}, 400

        if status:
            status = status.lower()
            data['status'] = status
            check_status = True
        else:
            data['status'] = ""
            check_status = False

        if not task:
            data['task'] = ""

        error = basic_validations(data, check_status=check_status)
        if error:
            return {'error': error}, 400

        error = update_todo(conn, transaction_ids, status, task, due_date)
        if error:
            return {'error': error}, 500

        return {}

# Custom 404 page for any other endpoints
@app.errorhandler(404)
def http_error_handler(error):
    return render_template('404.html'), 404

api.add_resource(Status, '/status/')
api.add_resource(TODO, '/todo/', methods = ['GET', 'POST', 'PUT', 'DELETE'])

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)