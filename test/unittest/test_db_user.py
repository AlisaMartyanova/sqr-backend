import model
from test import conftest


class Test:

    emails = ['1234@sdf.com', '1234@sdf.com', 'sdfghj@sdf.com']

    def test_save_users(self):
        unique = set(self.emails)
        for e in self.emails:
            model.User.get_or_create(e)

        assert len(unique) == len(model.User.query.filter_by().all())
        conftest.pytest_unconfigure()

    def test_find_by_email(self):
        user = model.User.get_or_create(self.emails[0])
        user_found = model.User.find_by_email(self.emails[0])

        assert user.id == user_found.id
        assert user.email == user_found.email
        conftest.pytest_unconfigure()

    def test_find_by_id(self):
        user = model.User.get_or_create(self.emails[0])
        user_found = model.User.find_by_id(user.id)

        assert user.id == user_found.id
        assert user.email == user_found.email
        assert self.emails[0] == user_found.email
        conftest.pytest_unconfigure()

