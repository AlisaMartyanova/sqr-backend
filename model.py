import datetime
from typing import Optional, Iterable, List

from flask_restful import abort

from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(256), unique=True, nullable=False)

    @classmethod
    def find_by_email(cls, email) -> Optional['User']:
        return cls.query.filter_by(email=email).first()

    @classmethod
    def ensure_all_users_exist(cls, emails: Iterable[str]) -> List['User']:
        users = []
        failed_users = []
        for email in set(emails):
            # SELECT ... WHERE email IN [...]; but I am lazy
            user = cls.find_by_email(email)
            if not user:
                failed_users.append(email)
            else:
                users.append(user)
        if len(failed_users) > 0:
            failed_users_str = "Cannot find users with emails: " + (", ".join(failed_users))
            raise abort(400, message=failed_users_str)
        return users

    @classmethod
    def get_or_create(cls, email):
        user: Optional[User] = cls.query.filter_by(email=email).first()
        if user is None:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        return user


    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    members = db.Column(db.Integer)
    creator = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) 
    name = db.Column(db.String(256))
    gift_date = db.Column(db.DateTime, nullable=True) 
    location = db.Column(db.String(256))
    members_assigned = db.Column(db.Boolean)

    @classmethod
    def create_with_memberships(cls, creator_id, name, gift_date, location: datetime.datetime, members: List[User]):
    # def create_with_memberships(cls, creator_id, name, gift_date, location, members):
        new_event = Event(
            members=len(members),
            creator=creator_id,
            name=name,
            gift_date=gift_date,
            location=location,
            members_assigned=False
        )
        db.session.add(new_event)
        db.session.commit()  # fetch ID
        for member in members:
            new_event_mem = Membership(
                user_id=member.id,
                event_id=new_event.id,
                status="pending"
            )
            db.session.add(new_event_mem)
        db.session.commit()
        return new_event

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def update_members_assigned(cls, id, state):
        event = cls.query.filter_by(id=id).first()
        event.members_assigned = state
        # return {'message': 'Event members assigned state was successfully edited'}


class Membership(db.Model):
    __tablename__ = 'event_members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, server_default="pending") 
    asignee = db.Column(db.Integer, db.ForeignKey("users.id")) 
    wishlist = db.Column(db.Text)

    @classmethod
    def find_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def find_by_user_event(cls, user_id, event_id):
        return cls.query.filter_by(user_id=user_id, event_id=event_id).first()

    @classmethod
    def update_status(cls, user_id, event_id, status):

        event = cls.query.filter_by(user_id=user_id, event_id=event_id).first()
        event.status = status
        db.session.commit()
        return {'message': 'Event status was changed to ' + status}

    @classmethod
    def update_assignee(cls, user_id, event_id, assignee):
        event = cls.query.filter_by(user_id=user_id, event_id=event_id).first()
        event.asignee = assignee
        db.session.commit()
        # return {'message': 'Event assignee was successfully edited'}

    @classmethod
    def update_wishlist(cls, user_id, event_id, wish):
        event = cls.query.filter_by(user_id=user_id, event_id=event_id).first()
        event.wishlist = wish
        db.session.commit()
        return {'message': 'Event wish list was successfully edited'}

    @classmethod
    def get_accepted_event(cls, event_id):
        return cls.query.filter_by(event_id=event_id, status='accepted').all()


