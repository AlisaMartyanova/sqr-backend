import requests
import json
from datetime import datetime
from os import environ
from app import app
from test import conftest
import model


class Test:
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
        'members': ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com']
    }

    def test_blank_token(self):
        response = app.test_client().patch('/assignee')
        assert json.loads(response.data.decode('utf-8')) == {'message': {'token': 'This field cannot be blank'}}

    def test_invalid_token(self):
        response = app.test_client().patch('/assignee', headers={'token': 'token'})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Invalid Firebase ID Token'}

    def test_blank_event(self):
        response = app.test_client().patch('/assignee', headers={'token': self.token})
        assert json.loads(response.data.decode('utf-8')) == {'message': {'event_id': 'This field cannot be blank'}}

    def test_wrong_event(self):
        response = app.test_client().patch('/assignee', headers={'token': self.token},
                                           json={'event_id': self.event_info['wrong_event_id']})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'No events found'}

    def test_wrong_creator(self):
        conftest.pytest_unconfigure()
        member = model.User.get_or_create(self.event_info['members'][0])
        model.User.get_or_create(self.data['email'])
        event = model.Event.create_with_memberships(member.id,
                                                    self.event_info['event_name'], self.event_info['date'],
                                                    self.event_info['place'],
                                                    [model.User.find_by_email(self.data['email'])])
        response = app.test_client().patch('/assignee', headers={'token': self.token}, json={'event_id': event.id})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Only creator can perform this action'}

    def test_not_enough_participants(self):
        conftest.pytest_unconfigure()
        event = model.Event.create_with_memberships(model.User.get_or_create(self.data['email']).id,
                                                    self.event_info['event_name'], self.event_info['date'],
                                                    self.event_info['place'], [])
        response = app.test_client().patch('/assignee', headers={'token': self.token}, json={'event_id': event.id})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Not enough participants'}

    def test_participants_assigned(self):
        conftest.pytest_unconfigure()
        member = model.User.get_or_create(self.event_info['members'][0])
        event = model.Event.create_with_memberships(model.User.get_or_create(self.data['email']).id,
                                                    self.event_info['event_name'], self.event_info['date'],
                                                    self.event_info['place'], [member])
        model.Membership.update_status(member.id, event.id, "accepted")
        response = app.test_client().patch('/assignee', headers={'token': self.token}, json={'event_id': event.id})
        assert json.loads(response.data.decode('utf-8')) == {'message': 'Participants assigned'}
