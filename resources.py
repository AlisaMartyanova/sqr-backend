import firebase_admin
from firebase_admin import auth, exceptions, credentials
from flask_restful import Resource, reqparse
from flask import send_from_directory, jsonify, json
import model
import os
from datetime import datetime
import app
from app import db
import _sqlite3
import sqlalchemy

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

token_parser = reqparse.RequestParser()
token_parser.add_argument('token', help='This field cannot be blank', required=True, location='headers')

event_parser = reqparse.RequestParser()
event_parser.add_argument('name', help='This field cannot be blank', required=True, location='args')
event_parser.add_argument('gift_date', help='This field cannot be blank', required=True, location='args')
event_parser.add_argument('location', help='This field cannot be blank', required=True, location='args')
event_parser.add_argument('members', help='This field cannot be blank', required=True, action='append', location='args')

invitation_parser = reqparse.RequestParser()
invitation_parser.add_argument('status', help='This field cannot be blank', required=True, location='args')
invitation_parser.add_argument('event_id', help='This field cannot be blank', required=True, location='args')

wishlist_parser = reqparse.RequestParser()
wishlist_parser.add_argument('event_id', help='This field cannot be blank', required=True, location='args')
wishlist_parser.add_argument('wishlist', help='This field cannot be blank', required=True, location='args')

assignee_parser = reqparse.RequestParser()
assignee_parser.add_argument('event_id', help='This field cannot be blank', required=True, location='args')


# verifies token and get user by this token
def get_user_by_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
    except auth.InvalidIdTokenError:
        return {'message': 'Invalid ID token.'}, 401

    uid = decoded_token['uid']

    try:
        firebase_user = auth.get_user(uid)
    except auth.UserNotFoundError as err:
        return {'message': 'Firebase user not found by UID.'}, 401

    return firebase_user, 200


# check if user exist in database
def check_user(user_email):
    if model.UserModel.find_by_email(user_email) is None:
        return False
    return True


# add user to database
def add_user(user_email):
    if not check_user(user_email):
        try:
            new_user = model.UserModel(
                email=user_email
            )
            new_user.save_to_db()
            return {'message': 'User was saved'}, 200
        except Exception as e:
            return {'message': str(e)}, 500
    return {'message': 'User was logged in'}, 200


# get user id
def get_user(user_email):
    if not check_user(user_email):
        return {'message': 'No such user'}, 500
    try:
        id = model.UserModel.find_by_email(user_email).id
    except Exception as e:
        return {'message': str(e)}, 500
    return id, 200


class UserLogin(Resource):

    def post(self):
        token = token_parser.parse_args()['token']
        cur_user = get_user_by_token(token)
        if cur_user[1] != 200:
            return cur_user
        message = add_user(cur_user[0].email)
        return message


class Event(Resource):

    def post(self):
        try:
            token = token_parser.parse_args()['token']
        except:
            return {'message': 'Wrong request arguments'}, 400

        cur_user = get_user_by_token(token)
        if cur_user[1] != 200:
            return cur_user
        cur_user_id = get_user(cur_user[0].email)
        if cur_user_id[1] != 200:
            return cur_user_id

        try:
            event = event_parser.parse_args()
            event_name = event['name']
            event_date = event['gift_date']
            event_location = event['location']
            event_members = event['members']
        except:
            return {'message': 'Wrong request arguments'}, 400

        members = []
        non_existed = []
        for m in event_members:
            if check_user(m):
                members.append(m)
            else:
                non_existed.append(m)

        try:
            new_event = model.EventsModel(
                members=len(members),
                creator=cur_user_id[0],
                name=event_name,
                gift_date=datetime.strptime(event_date, '%Y-%m-%d'),
                location=event_location,
                members_assigned=False
            )
            new_event.save_to_db()
            db.session.flush()
            event_id = new_event.id
        except Exception as e:
            return {'message': str(e)}, 500

        for i in members:
            try:
                new_event_mem = model.EventMembersModel(
                    user_id=get_user(i)[0],
                    event_id=event_id,
                    status="pending"
                )
                new_event_mem.save_to_db()
                db.session.flush()
            except Exception as e:
                return {'message': str(e)}, 500
        try:
            db.session.commit()
        except Exception as e:
            return {'message': str(e)}, 500

        return {'event_id': event_id, 'non-existing_users': non_existed}, 200

    def get(self):
        try:
            token = token_parser.parse_args()['token']
        except:
            return {'message': 'Wrong request arguments'}, 400

        cur_user = get_user_by_token(token)
        if cur_user[1] != 200:
            return cur_user
        cur_user_id = get_user(cur_user[0].email)
        if cur_user_id[1] != 200:
            return cur_user_id

        cur_user_events = []
        try:
            events = model.EventMembersModel.find_by_user(cur_user_id[0])
        except (sqlalchemy.exc.InterfaceError, AttributeError):
            return {'message': 'Wrong database request, could not find event'}, 500

        for i in events:
            try:
                ev = model.EventsModel.find_by_id(i.event_id)
            except (sqlalchemy.exc.InterfaceError, AttributeError):
                return {'message': 'Wrong database request, could not find event'}, 500

            assignee = None
            assignee_wishlist = None
            if ev.members_assigned:
                try:
                    assignee = model.UserModel.find_by_id(i.asignee).email
                    assignee_wishlist = model.EventMembersModel.find_by_user_event(i.asignee, i.event_id).wishlist
                except (sqlalchemy.exc.InterfaceError, AttributeError):
                    return {'message': 'Wrong database request, could not find assignee or wishlist'}, 500

            event = {
                'event_id': i.event_id,
                'invitations': ev.members,
                'accepted_members': len(model.EventMembersModel.get_accepted_event(i.event_id)),
                'creator': model.UserModel.find_by_id(ev.creator).email,
                'name': ev.name,
                'gift_date': str(ev.gift_date),
                'location': ev.location,
                'current_user_wishlist': i.wishlist,
                'members_assigned': ev.members_assigned,
                'assignee_email': assignee,
                'assignee_wishlist': assignee_wishlist,
                'status': model.EventMembersModel.find_by_user_event(cur_user_id[0], i.event_id).status
            }
            cur_user_events.append(event)
        return cur_user_events, 200


class Invitation(Resource):

    def patch(self):
        try:
            token = token_parser.parse_args()['token']
        except:
            return {'message': 'Wrong request arguments'}, 400

        cur_user = get_user_by_token(token)
        if cur_user[1] != 200:
            return cur_user
        cur_user_id = get_user(cur_user[0].email)
        if cur_user_id[1] != 200:
            return cur_user_id
        try:
            invitation = invitation_parser.parse_args()
            invitation_status = invitation['status']
            event_id = invitation['event_id']
        except:
            return {'message': 'Wrong request arguments'}, 400

        if invitation_status not in ['accepted', 'pending', 'denied']:
            return {'message': 'Wrong status: it should be "accepted", "pending" or "denied"'}, 400

        try:
            message = model.EventMembersModel.update_status(cur_user_id[0], event_id, invitation_status)
        except Exception as e:
            return {'message': str(e)}, 500

        return message, 200


class Wishlist(Resource):

    def patch(self):
        try:
            token = token_parser.parse_args()['token']
        except:
            return {'message': 'Wrong request arguments'}, 400

        cur_user = get_user_by_token(token)
        if cur_user[1] != 200:
            return cur_user
        cur_user_id = get_user(cur_user[0].email)
        if cur_user_id[1] != 200:
            return cur_user_id

        try:
            wishlist = wishlist_parser.parse_args()
            wish = wishlist['wishlist']
            event_id = wishlist['event_id']
        except:
            return {'message': 'Wrong request arguments'}, 400

        try:
            message = model.EventMembersModel.update_wishlist(cur_user_id[0], event_id, wish)
        except Exception as e:
            return {'message': str(e)}, 500

        return message, 200


def move_left(list):
    l = list[1:]
    l.append(list[0])
    return l


class AssignGiftees(Resource):

    def patch(self):
        try:
            token = token_parser.parse_args()['token']
        except:
            return {'message': 'Wrong request arguments'}, 400

        cur_user = get_user_by_token(token)
        if cur_user[1] != 200:
            return cur_user
        cur_user_id = get_user(cur_user[0].email)
        if cur_user_id[1] != 200:
            return cur_user_id

        try:
            event = assignee_parser.parse_args()
            event_id = event['event_id']
        except:
            return {'message': 'Wrong request arguments'}, 400

        try:
            event = model.EventsModel.find_by_id(event_id)
        except (sqlalchemy.exc.InterfaceError, AttributeError):
            return {'message': 'Wrong database request, could not find model'}, 500

        if event is None:
            return {'message': 'No events found'}, 500

        if event.creator != cur_user_id[0]:
            return {'message': 'Only creator can perform this action'}, 403

        try:
            accepted = model.EventMembersModel.get_accepted_event(event_id)
        except (sqlalchemy.exc.InterfaceError, AttributeError):
            return {'message': 'Wrong database request, could not find accepted events'}, 500

        if len(accepted) <= 1:
            return {'message': 'Not enough participants'}, 406

        participants = []
        for a in accepted:
            participants.append(a.user_id)
        assignee = move_left(participants)

        try:
            model.EventsModel.update_members_assigned(event_id, True)
            db.session.flush()
        except Exception as e:
            return {'message': str(e)}, 500

        for i in range(len(participants)):
            try:
                model.EventMembersModel.update_assignee(participants[i], event_id, assignee[i])
                db.session.flush()
            except Exception as e:
                return {'message': str(e)}, 500

        try:
            db.session.commit()
        except Exception as e:
            return {'message': str(e)}, 500

        return {'message': 'Participants assigned'}, 200
