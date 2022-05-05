import model
from test import conftest
from enum import Enum
from datetime import datetime

class Test:
    emails = ['12834@sdf.com', '1235@sdf.com', 'sdf8ghj@sdf.com']
    users = []
    event_info = {
        'event_name': 'Event1',
        'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
        'place': 'University',
        'state': True,
        'status': "accepted"
    }
    def create_user(self, email):
        self.users.append(model.User.get_or_create(email))
        user = model.User.get_or_create(email).id
        return user

    def create_event(self):
        self.users = []
        for e in self.emails:
            self.users.append(model.User.get_or_create(e))
        return model.Event.create_with_memberships(self.users[0].id, self.event_info['event_name'],
                                                   self.event_info['date'], self.event_info['place'], 
                                                   self.users)

    def test_find_by_user(self):
        conftest.pytest_unconfigure()
        event = self.create_event()
        user_id = self.users[0].id
        found = model.Membership.find_by_user(user_id)[0]

        assert event.id == found.event_id
        conftest.pytest_unconfigure()

    def test_find_by_user_event(self):
        event_id = self.create_event().id
        user_id = self.users[0].id
        found = model.Membership.find_by_user_event(user_id, event_id)
        
        assert event_id == found.event_id
        conftest.pytest_unconfigure()


    def test_update_status(self):
        event_id = self.create_event().id
        user_id = self.users[0].id
        model.Membership.update_status(user_id, event_id, self.event_info['status'])

        mem = model.Membership.find_by_user_event(user_id, event_id).status
        assert mem == self.event_info['status']
        conftest.pytest_unconfigure()

    def test_update_assignee(self):
        event = self.create_event()
        assignee = self.create_user("natasha@email.com")

        model.Membership.update_assignee(self.users[0].id, event.id, assignee)
        event_assignee_id = model.Membership.find_by_user_event(self.users[0].id, event.id).asignee
        assignee_id = assignee

        assert assignee_id == event_assignee_id
        conftest.pytest_unconfigure()

    def test_update_wishlist(self):
        event_id = self.create_event().id
        user_id = self.users[0].id
        wish = "I want to be a happy princess"
        model.Membership.update_wishlist(user_id, event_id, wish)
    
        event_wish = model.Membership.find_by_user_event(user_id, event_id).wishlist
        assert event_wish == wish
        conftest.pytest_unconfigure()

    def test_get_accepted_event(self):
        event = self.create_event()
        user_id = self.users[0].id
        model.Membership.update_status(user_id, event.id, "accepted")
        
        events = model.Membership.get_accepted_event(event.id)
        user_event = events[0].user_id


        assert user_event == user_id
        conftest.pytest_unconfigure()
        

