from app import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(256), unique=True, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()


class EventsModel(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    members = db.Column(db.Integer)
    creator = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False) 
    name = db.Column(db.String(256))
    gift_date = db.Column(db.DateTime, nullable=True) 
    location = db.Column(db.String(256))
    members_assigned = db.Column(db.Boolean)

    def save_to_db(self):
        db.session.add(self)
        # db.session.commit()
        # return self.id

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def update_members(cls, id, num):
        db.session.query(cls).filter(id=id).update({'members': (cls.members + num)})
        db.session.commit()
        return {'message': 'Event members was successfully edited'}

    @classmethod
    def update_members_assigned(cls, id, state):
        db.session.query(cls).filter(id=id).update({'members_assigned': state})
        # db.session.commit()
        # return {'message': 'Event members assigned state was successfully edited'}


class EventMembersModel(db.Model):
    __tablename__ = 'event_members'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, server_default="pending") 
    asignee = db.Column(db.Integer, db.ForeignKey("users.id")) 
    wishlist = db.Column(db.Text)

    def save_to_db(self):
        db.session.add(self)
        # db.session.commit()
        # return self.id

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
        # db.session.commit()
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
