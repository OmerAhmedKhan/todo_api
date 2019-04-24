import unittest
import requests
import json


ENDPOINT= "http://127.0.0.1:5000/todo/"
class TestAPI(unittest.TestCase):

    # def __init__(self, *args, **kwargs):
    #     super(TestAPI, self).__init__(*args, **kwargs)]

    def test_create_todo(self):
        status = ["done", "not done", "done"]
        task = ["shopping", "fixing", "dishes"]
        due_date = ["", "09-09-2019", "2-12-2020"]
        for i in range(0,3):
            data = {
                'status': status[i],
                'task': task[i],
                'due_date': due_date[i]
            }
            response = requests.post(ENDPOINT, data)
            assert response.status_code == 201

    def test_create_todo_invalid(self):
        status = ['done', "", 'done']
        task = ["", "fixing", "dishes"]
        due_date = ["", "09-09-2019", "2--2020"]
        for i in range(0, 3):
            data = {
                'status': status[i],
                'task': task[i],
                'due_date': due_date[i]
            }
            if i == 0 :
                data.pop('task')
            response = requests.post(ENDPOINT, data)
            assert response.status_code == 400

    def test_get_all_todo(self):
        response = requests.get(ENDPOINT)
        assert response.status_code == 200

    def test_filter_by_status(self):
        status = "~done~"
        response = requests.get("{}?status={}".format(ENDPOINT, status))
        rows = json.loads(response.content)
        assert len(rows) > 0
        assert response.status_code == 200
        for row in rows:
            assert row.get("status") == "done"

    def test_filter_by_due_date(self):
        self.test_create_todo()
        due_date = "09-09-2019"
        response = requests.get("{}?due_date={}".format(ENDPOINT, due_date))
        rows = json.loads(response.content)
        assert len(rows) == 1
        assert response.status_code == 200

    def test_filter_neagtive(self):
        response = requests.get("{}?abc={}".format(ENDPOINT, "abc"))
        assert response.status_code == 400

        response = requests.get("{}?status={}".format(ENDPOINT, "abc"))
        assert response.status_code == 400

        response = requests.get("{}?due_date={}".format(ENDPOINT, "abc"))
        assert response.status_code == 400

    def test_update(self):
        data = {
            'status': "done",
            'task': "abc"
        }
        response = requests.post(ENDPOINT, data)
        assert response.status_code == 201



    def test_update_negative(self):
        w=1

    def test_delete_by_transaction_id(self):
        data = {
            'status': "done",
            'task': "abc"
        }
        response = requests.post(ENDPOINT, data)
        assert response.status_code == 201

        response = requests.get(ENDPOINT)
        assert response.status_code == 200

        transaction_id = json.loads(response.content)[0].get("transaction_id")
        assert response.status_code == 200
        data = {
            "transaction_id": transaction_id
        }
        response = requests.delete(ENDPOINT, data=data)
        assert response.status_code == 200


    def test_delete_by_status(self):
        data = {
            'status': "done",
            'task': "abc"
        }
        response = requests.post(ENDPOINT, data)
        assert response.status_code == 201

        data.pop("task")
        response = requests.delete(ENDPOINT, data=data)
        assert response.status_code == 200

        response = requests.get(ENDPOINT)
        assert response.status_code == 200

        rows = json.loads(response.content)
        assert len(rows) > 0
        for row in rows:
            assert row.get("status") == "not done"


    def test_delete_by_due_date(self):
        data = {
            'status': "done",
            'task': "abc",
            'due_date': "12-12-2012"
        }
        response = requests.post(ENDPOINT, data)
        assert response.status_code == 201

        data = {'due_date': "12-12-2012"}
        response = requests.delete(ENDPOINT, data=data)
        assert response.status_code == 200

        response = requests.get(ENDPOINT)
        assert response.status_code == 200

        rows = json.loads(response.content)
        assert len(rows) > 0
        for row in rows:
            assert row.get("due_date") != "12-12-2012"


if __name__ == '__main__':
    response = requests.delete("{}".format(ENDPOINT))
    assert response.status_code == 200
    unittest.main()
