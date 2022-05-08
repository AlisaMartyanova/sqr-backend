import requests
import json
from datetime import datetime
from os import environ
from app import app
from test import conftest
import model


class Test:
    path = '/wishlist'
    data = {
        "email": environ.get('TEST_USER_EMAIL'),
        "password": environ.get('TEST_USER_PASSWORD'),
        "returnSecureToken": True
    }
    resp = requests.post(environ.get('TEST_URL'), data=data)
    token = str(resp.json()['idToken'])

    event_info = {
        'event_name': 'Event1',
        'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
        'place': 'University',
        'state': True,
        'wishlist': "This is my wishlist",
        'wrong_event_id': 0,
        'members': ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com'],
        'wrong_status': 'wrong',
        'correct_status': 'denied'
    }

    def test_blank_token(self):
        response = app.test_client().patch(self.path)
        assert json.loads(response.data.decode('utf-8')) == {
            'message': {'token': 'This field cannot be blank'}}

    def test_invalid_token(self):
        response = app.test_client().patch(self.path, 
            headers={'token': 'token'})
        assert json.loads(response.data.decode('utf-8')) == {
            'message': 'Invalid Firebase ID Token'}

    def test_blank_field(self):
        response = app.test_client().patch(self.path, 
            headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8')) == {'message': 
                    'Wrong request arguments'}

    def test_correct(self):
        conftest.pytest_unconfigure()
        member = model.User.get_or_create(self.event_info['members'][0])
        event = model.Event.create_with_memberships(
                    model.User.get_or_create(self.data['email']).id,
                    self.event_info['event_name'], self.event_info['date'],
                    self.event_info['place'], [member])
        response = app.test_client().patch(self.path, 
                        headers={'token': self.token},
                        json={'wishlist': self.event_info['wishlist'], 
                        'event_id': event.id})
        assert json.loads(response.data.decode('utf-8')) == {
            'message': 'Event wish list was successfully edited'}

        response = app.test_client().get('/events', 
            headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8'
            ))[0]['current_user_wishlist'] == self.event_info['wishlist']
