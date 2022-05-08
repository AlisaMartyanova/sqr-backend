import model
from test import conftest
from enum import Enum
from datetime import datetime


class Test:
    event_info = {
        'creator': 'creator@mail.com',
        'event_name': 'Event1',
        'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
        'place': 'University',
        'state': True,
        'members': ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com'],
        'status': 'denied'
    }

    def create_event(self):
        return model.Event.create_with_memberships(
            model.User.get_or_create(self.event_info['creator']).id,
            self.event_info['event_name'], self.event_info['date'],
            self.event_info['place'], [model.User.get_or_create(u)
            for u in self.event_info['members']])

    def test_find_by_user(self):
        conftest.pytest_unconfigure()
        event = self.create_event()
        user_id = model.User.get_or_create(self.event_info['creator']).id
        found = model.Membership.find_by_user(user_id)[0]

        assert event.id == found.event_id

    def test_find_by_user_event(self):
        conftest.pytest_unconfigure()
        event_id = self.create_event().id
        user_id = model.User.get_or_create(self.event_info['creator']).id
        found = model.Membership.find_by_user_event(user_id, event_id)

        assert event_id == found.event_id

    def test_update_status(self):
        conftest.pytest_unconfigure()
        event_id = self.create_event().id
        user_id = model.User.get_or_create(self.event_info['creator']).id
        model.Membership.update_status(user_id, event_id, 
                                       self.event_info['status'])

        mem = model.Membership.find_by_user_event(user_id, event_id).status
        assert mem == self.event_info['status']

    def test_update_assignee(self):
        conftest.pytest_unconfigure()
        event = self.create_event()
        assignee = model.User.get_or_create(self.event_info['members'][0]).id

        model.Membership.update_assignee(model.User.get_or_create(
            self.event_info['creator']).id, event.id, assignee)
        event_assignee_id = model.Membership.find_by_user_event(
                model.User.get_or_create(self.event_info['creator']).id,
                event.id).asignee
        assignee_id = assignee

        assert assignee_id == event_assignee_id

    def test_update_wishlist(self):
        conftest.pytest_unconfigure()
        event_id = self.create_event().id
        user_id = model.User.get_or_create(self.event_info['creator']).id
        wish = "I want to be a happy princess"
        model.Membership.update_wishlist(user_id, event_id, wish)

        event_wish = model.Membership.find_by_user_event(user_id, 
                     event_id).wishlist
        assert event_wish == wish

    def test_get_accepted_event(self):
        conftest.pytest_unconfigure()
        event = self.create_event()
        user_id = model.User.get_or_create(self.event_info['creator']).id
        events = model.Membership.get_accepted_event(event.id)
        user_event = events[0].user_id

        assert user_event == user_id
