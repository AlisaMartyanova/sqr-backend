from datetime import datetime
from test.unittest import conftest
import model
from app import db


class Test:
    emails = ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com']
    users = []
    event_info = {
        'event_name': 'Event1',
        'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
        'place': 'University',
        'state': True
    }

    def create_event(self):
        self.users = []
        for e in self.emails:
            self.users.append(model.User.get_or_create(e))
        return model.Event.create_with_memberships(self.users[0].id, self.event_info['event_name'],
                                                   self.event_info['date'], self.event_info['place'], self.users)

    def test_create_with_memberships(self):
        event = self.create_event()
        assert event.members == len(self.users)
        assert event.creator == self.users[0].id
        assert event.name == self.event_info['event_name']
        assert event.gift_date == self.event_info['date']
        assert event.location == self.event_info['place']

        assert len(model.Membership.query.filter_by().all()) == len(self.users)
        conftest.pytest_unconfigure()

    def test_find_by_id(self):
        event = self.create_event()
        found = model.Event.find_by_id(event.id)

        assert event.id == found.id
        assert event.members == found.members
        assert event.creator == found.creator
        assert event.name == found.name
        assert event.gift_date == found.gift_date
        assert event.location == found.location
        conftest.pytest_unconfigure()

    def test_update_members_assigned(self):
        event = self.create_event()
        model.Event.update_members_assigned(event.id, self.event_info['state'])
        db.session.commit()

        event = model.Event.find_by_id(event.id)
        assert event.members_assigned == self.event_info['state']
        conftest.pytest_unconfigure()

