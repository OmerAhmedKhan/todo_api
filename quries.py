GET_ALL = "SELECT * FROM todo_list"
CREATE_TODO = "INSERT INTO todo_list VALUES (?, ?, ?, ?, ?)"
DELETE_TODO = "DELETE FROM todo_list WHERE transaction_id=?"
DELETE_TODO_DUE_DATA = "DELETE FROM todo_list WHERE due_date='{}'"
DELETE_TODO_STATUS = "DELETE FROM todo_list WHERE status='{}'"
DELETE_ALL = "DELETE FROM todo_list"
IS_TABLE_EXSIST = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'"