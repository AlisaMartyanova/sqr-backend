import model
from test import conftest


class Test:

    def test_save_users(self):
        emails = ['1234@sdf.com', '1234@sdf.com', 'sdfghj@sdf.com']
        unique = set(emails)
        for e in emails:
            model.User.get_or_create(e)

        assert len(unique) == len(model.User.query.filter_by().all())
        conftest.pytest_unconfigure()

    def test_find_by_email(self):
        user_email = "asdfgh@sdfg.com"
        user = model.User.get_or_create(user_email)
        user_found = model.User.find_by_email(user_email)

        assert user.id == user_found.id
        assert user.email == user_found.email
        conftest.pytest_unconfigure()

    def test_find_by_id(self):
        user_email = "asdfgh@sdfg.com"
        user = model.User.get_or_create(user_email)
        user_found = model.User.find_by_id(user.id)

        assert user.id == user_found.id
        assert user.email == user_found.email
        conftest.pytest_unconfigure()

    # def test_ensure_all_users_exist(self):
    #     existed = ['1234@sdf.com', '1234@sdf.com', 'sdfghj@sdf.com']
    #     check = ['1234@sdf.com', 'sdfghj@sdf.com']

