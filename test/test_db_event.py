from datetime import datetime
from test import conftest
import model


class Test:

    def test_create_with_memberships(self):
        emails = ['1234@sdf.com', 'sdfghj@sdf.com', 'sdfhnjjhghj@kjh.com']
        users = []
        for e in emails:
            users.append(model.User.get_or_create(e))

        event = model.Event.create_with_memberships(users[0].id, 'Event1',
                                                    datetime.strptime('2022-02-25', '%Y-%m-%d'), 'University', users)
        assert event.members == len(users)
        assert event.creator == users[0].id
        assert event.name == 'Event1'
        assert event.gift_date == datetime.strptime('2022-02-25', '%Y-%m-%d')
        assert event.location == 'University'

        assert len(model.Membership.query.filter_by().all()) == len(users)
        conftest.pytest_unconfigure()

