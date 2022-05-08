from datetime import datetime
from test import conftest
import model
from app import db


class Test:
    event_info = {
        'creator': 'creator@mail.com',
        'event_name': 'Event1',
        'date': datetime.strptime('2022-02-25', '%Y-%m-%d'),
        'place': 'University',
        'state': True,
        'members': ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com']
    }

    def create_event(self):
        return model.Event.create_with_memberships(
            model.User.get_or_create(self.event_info['creator']).id,
            self.event_info['event_name'], self.event_info['date'],
            self.event_info['place'], [model.User.get_or_create(u)
            for u in self.event_info['members']])

    def test_create_with_memberships(self):
        conftest.pytest_unconfigure()
        event = self.create_event()
        assert event.members == len(self.event_info['members'])+1
        assert event.creator == model.User.get_or_create(
            self.event_info['creator']).id
        assert event.name == self.event_info['event_name']
        assert event.gift_date == self.event_info['date']
        assert event.location == self.event_info['place']
        assert len(model.Membership.query.filter_by().all()) == len(
            self.event_info['members']) + 1

    def test_find_by_id(self):
        conftest.pytest_unconfigure()
        event = self.create_event()
        found = model.Event.find_by_id(event.id)

        assert event.id == found.id
        assert event.members == found.members
        assert event.creator == found.creator
        assert event.name == found.name
        assert event.gift_date == found.gift_date
        assert event.location == found.location

    def test_update_members_assigned(self):
        conftest.pytest_unconfigure()
        event = self.create_event()
        model.Event.update_members_assigned(event.id, self.event_info['state'])
        db.session.commit()

        event = model.Event.find_by_id(event.id)
        assert event.members_assigned == self.event_info['state']
