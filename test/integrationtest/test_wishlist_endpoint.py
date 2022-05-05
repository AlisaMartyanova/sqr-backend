# import requests
# import json
# from datetime import datetime
# from os import environ
# from app import app
# from test import conftest


# class Test:
#     data = {
#         "email": environ.get('TEST_USER_EMAIL'),
#         "password": environ.get('TEST_USER_PASSWORD'),
#         "returnSecureToken": True
#     }
#     resp = requests.post(environ.get('TEST_URL'), data=data)
#     token = str(resp.json()['idToken'])

#     emails = ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com']
#     users = []
#     event_info = {
#         'event_name': 'Event1',
#         'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
#         'place': 'University',
#         'state': True,
#         'wishlist': "This is my wishlist"
#     }

#     def test_patch(self):
#         response = app.test_client().patch('/wishlist')
#         assert json.loads(response.data.decode('utf-8')) == {'message': {'token': 'This field cannot be blank'}}

#         response = app.test_client().patch('/wishlist', headers={'token': 'token'})
#         assert json.loads(response.data.decode('utf-8')) == {'message': 'Invalid Firebase ID Token'}

#         response = app.test_client().patch('/wishlist', headers={'token': self.token})
#         assert json.loads(response.data.decode('utf-8')) == {'message': 'Wrong request arguments'}

#         response = app.test_client().post('/events', headers={'token': self.token},
#                                           json={'name': self.event_info['event_name'],
#                                                 'gift_date': '2022-02-25',
#                                                 'location': self.event_info['place'], 'members': self.data['email']})
#         id = json.loads(response.data.decode('utf-8'))['id']
#         response = app.test_client().patch('/wishlist', headers={'token': self.token},
#                                            json={'wishlist': self.event_info['wishlist'], 'event_id': id})
#         assert json.loads(response.data.decode('utf-8')) == {'message': 'Event wish list was successfully edited'}

#         response = app.test_client().get('/events', headers={'token': self.token})
#         assert json.loads(response.data.decode('utf-8'))[0]['current_user_wishlist'] == self.event_info['wishlist']

#         conftest.pytest_unconfigure()