import logging
from datetime import datetime
import uuid
from quries import GET_ALL, CREATE_TODO, IS_TABLE_EXSIST, \
    DELETE_TODO, DELETE_ALL, DELETE_TODO_DUE_DATA, DELETE_TODO_STATUS

FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(FORMAT)
logging.basicConfig(filename='error.log',level=logging.ERROR, format=FORMAT)
error_logger = logging.getLogger('error')
logger = logging.getLogger('activity')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('activity.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
DATABASE= "todo.db"




def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def create_table(conn):
    cursor = conn.cursor()
    result = cursor.execute(IS_TABLE_EXSIST.format("todo_list"))
    if result.fetchone():
        return

    # Create table
    cursor.execute("CREATE TABLE todo_list (status text, task text, due_date text, created_timestamp text, transaction_id text)")
    # Save (commit) the changes
    conn.commit()

    return


def str_to_date(date):
    return datetime.strptime(date, "%d-%m-%Y")


def get_datetime_now():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def fix_due_date(date):
    return str(datetime.strptime(date, "%d-%m-%Y")).split(" ")[0]

def validate_due_date(due_date):

    error = ""
    try:
        str_to_date(due_date)
    except:
        error = "Invalid Date"
        error_logger.error(error)
        return error

    return error

def validate_todo(status, task, due_date="", check_status=True):
    error = ""
    if not isinstance(status, str):
        error = "Invalid Status type"
        error_logger.error("Invalid Status type")
        return error

    if check_status:
        if status not in ["done", "not done"]:
            error = "Not a correct status, status can only be 'done' or 'not done'"
            error_logger.error(error)
            return error

    if not isinstance(task, str):
        error = "Invalid Task type"
        error_logger.error(error)
        return error

    if not isinstance(due_date, str):
        error = "Invalid Date type"
        error_logger.error(error)
        return error

    if due_date:
        error = validate_due_date(due_date)

    return error

def get_all(cursor):

    result = cursor.execute(GET_ALL)
    result = [dict(row) for row in result.fetchall()]
    return result


def search_todo(cursor, status, task, due_date=""):
    if not any([status, task, due_date]):
        error_logger.error("Status or Task not provided")
        return

    if all([status, task, due_date]):
        due_date = fix_due_date(due_date)
        cursor.execute("SELECT * FROM todo_list WHERE status='{}' AND task='{}' AND due_date='{}'"
                       .format(status, task, due_date))
    elif status and task:
        cursor.execute("SELECT * FROM todo_list WHERE status='{}' AND task='{}'".format(status, task))
    elif status:
        cursor.execute("SELECT * FROM todo_list WHERE status='{}'".format(status))
    elif task:
        cursor.execute("SELECT * FROM todo_list WHERE task='{}'".format(task))
    elif due_date:
        due_date = fix_due_date(due_date)
        cursor.execute("SELECT * FROM todo_list WHERE due_date='{}'".format(due_date))
    else:
        return

    return cursor.fetchall()


def create_todo(conn, status, task, due_date=""):
    cursor = conn.cursor()
    if not status and task:
        error_logger.error("Status or Task not provided")
        return

    if validate_todo(status, task, due_date):
        return

    if due_date:
        due_date = fix_due_date(due_date)

    try:
        cursor.execute(CREATE_TODO, (status, task, due_date, get_datetime_now(), str(uuid.uuid4())))
        result = conn.commit()
    except Exception as e:
        error = "Unable to add Todo task"
        error_logger.error("Unable to add Todo task due to: {}".format(str(e)))
        return error

    logger.info("Todo Task '{}' added with status '{}'".format(task, status))
    return result


def delete_due_date(conn, due_date):
    cursor = conn.cursor()
    if validate_due_date(due_date):
        return

    due_date = fix_due_date(due_date)
    try:
        cursor.execute(DELETE_TODO_DUE_DATA.format(due_date))
        result = conn.commit()
    except Exception as e:
        error = "Unable to delete Todo task"
        error_logger.error("Unable to delete Todo task due to: {}".format(str(e)))
        return error

    # result = cursor.rowcount
    # if not result:
    #     logger.info("There are no data with due_date {}".format(due_date))
    #     return result

    logger.info("Todo Task of due date {} is deleted".format(due_date))
    return result


def delete_status(conn, status):
    cursor= conn.cursor()
    if not status or not isinstance(status, str):
        error_logger.error('Status not provided or Invalid')
        return

    if status not in ["done", "not done"]:
        error_logger.error("Status {} is not valid".format(status))
        return

    try:
        cursor.execute(DELETE_TODO_STATUS.format(status))
        result = conn.commit()
    except Exception as e:
        error = "Unable to delete Todo task"
        error_logger.error("Unable to delete Todo task due to: {}".format(str(e)))
        return error

    # result = cursor.rowcount
    # if not result:
    #     logger.info("There are no data with status {}".format(status))
    #     return

    logger.info("Todo Tasks deleted with status {}".format(status))
    return


def delete_by_transaction_id(conn, transaction_ids):
    cursor= conn.cursor()
    if not isinstance(transaction_ids, list):
        error_logger.error('transaction id list not provided')
        return

    try:
        cursor.execute(DELETE_TODO, (transaction_ids))
        result = conn.commit()
    except Exception as e:
        error = "Unable to delete Todo task"
        error_logger.error("Unable to delete Todo task due to: {}".format(str(e)))
        return error

    logger.info("Todo Tasks deleted with transaction_id {}".format(transaction_ids))
    return


def delete_all(conn):
    cursor = conn.cursor()

    try:
        cursor.execute(DELETE_ALL)
        result = conn.commit()
    except Exception as e:
        error = "Unable to delete Todo task"
        error_logger.error("Unable to delete all Todo task due to: {}".format(str(e)))
        return error

    logger.info("ALL Todo Tasks are deleted")
    return result


def update_todo(conn, transaction_ids,status, task, due_date):

    cursor = conn.cursor()

    try:
        if all([status, task, due_date]):
            due_date = fix_due_date(due_date)
            cursor.execute("UPDATE todo_list SET status='{}', task='{}', due_date='{}' WHERE transaction_id='{}' "
                .format(status, task, due_date, transaction_ids))
        elif status and task:
            cursor.execute("UPDATE todo_list SET status='{}', task='{}' WHERE transaction_id='{}'"
                .format(status, task, transaction_ids))
        elif status:
            cursor.execute("UPDATE todo_list SET status='{}' WHERE transaction_id='{}'"
                .format(status, transaction_ids))
        elif task:
            cursor.execute("UPDATE todo_list SET task='{}' WHERE transaction_id='{}'"
                .format(task, transaction_ids))
        elif due_date:
            due_date = fix_due_date(due_date)
            cursor.execute("UPDATE todo_list SET due_date='{}' WHERE transaction_id='{}'".format(due_date, transaction_ids))
        else:
            return

    except Exception as e:
        error = "Unable to update Todo task"
        error_logger.error("Unable to delete all Todo task due to: {}".format(str(e)))
        return error

    return

