import logging
from flask import Flask
from flask_restful import Resource, Api
import sqlite3
from flask_restful import request
from flask import jsonify
from flask import render_template
from module import dict_factory, create_table, create_todo, get_all, validate_todo, search_todo, \
    delete_status, delete_due_date, delete_all, delete_by_transaction_id, update_todo

logging.basicConfig(filename='error.log',level=logging.ERROR)


# Sqlite3 in-memory storage
DATABASE= "todo.db"
conn = sqlite3.connect(DATABASE, check_same_thread=False)
conn.row_factory = dict_factory
cur = conn.cursor()
cursor = conn.cursor()

create_table(conn)

app = Flask(__name__)
api = Api(app)


# Global Variables
value_to_int= {}
hash_to_value = {}
counter = 1


def basic_validations(args, check_status=True):
    """Basic validations for arguments"""

    for k, v in args.items():
        if not k:
            if not isinstance(v, str):
                error = 'Argument parameter should only be a url'
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
    """ API for Redirect URL """

    def get(self):
        args = request.args.copy()
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

        if any([status, task, due_date]):
            resp = search_todo(cursor, status, task, due_date)
        else:
            resp = get_all(cursor)

        return jsonify(resp)

    def post(self):
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

        data = request.form.copy()
        status = data.get('status', "")
        task = data.get('task')
        due_date = data.get('due_date', "")
        transaction_ids = data.get("transaction_id")
        
        if transaction_ids:
            ids = transaction_ids.split(",")
            error = delete_by_transaction_id(conn, ids)
            if error:
                return {'error': error}, 400

            return {}

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

        if status:
            error = delete_status(conn, status)
            if error:
                return {'error': error}, 500
        elif due_date:
            error = delete_due_date(conn, due_date)
            if error:
                return {'error': error}, 500


        return {}


    def put(self):

        check_status = True
        data = request.form.copy()
        status = data.get('status', "")
        task = data.get('task')
        due_date = data.get('due_date', "")
        transaction_ids = data.get("transaction_id")

        if not transaction_ids:
            error = "Transaction ID not provided"
            return {'error': error}, 400

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




@app.errorhandler(404)
def http_error_handler(error):
    return render_template('404.html'), 404

api.add_resource(Status, '/status/')
api.add_resource(TODO, '/todo/', methods = ['GET', 'POST', 'PUT', 'DELETE'])

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)