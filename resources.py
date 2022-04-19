import firebase_admin
from firebase_admin import auth, exceptions, credentials
from flask_restful import Resource, reqparse
from flask import send_from_directory, jsonify, json
import model
import os
from datetime import datetime
import app

cred = credentials.Certificate("db/serviceAccountKey.json")
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
        return 'Invalid ID token.', 401

    uid = decoded_token['uid']

    try:
        firebase_user = auth.get_user(uid)
    except auth.UserNotFoundError as err:
        return 'Firebase user not found by UID.', 401

    return firebase_user


# check if user exist in database
def check_user(user_email):
    if model.UserModel.find_by_email(user_email) is None:
        return False
    return True


# add user to database and return his id
def get_user(user_email):
    if not check_user(user_email):
        new_user = model.UserModel(
            email=user_email
        )
        new_user.save_to_db()
    return model.UserModel.find_by_email(user_email).id


class UserLogin(Resource):

    def post(self):
        token = token_parser.parse_args()['token']
        cur_user = get_user_by_token(token)
        cur_user_id = get_user(cur_user.email)
        return {'message': 'User ' + cur_user.email + ' logged in'}, 200


class Event(Resource):

    def post(self):
        token = token_parser.parse_args()['token']
        cur_user = get_user_by_token(token)
        cur_user_id = get_user(cur_user.email)

        event = event_parser.parse_args()
        event_name = event['name']
        event_date = event['gift_date']
        event_location = event['location']
        event_members = event['members']



        members = []
        non_existed = []
        for m in event_members:
            if check_user(m):
                members.append(m)
            else:
                non_existed.append(m)

        new_event = model.EventsModel(
            members=len(members),
            creator=cur_user_id,
            name=event_name,
            gift_date=datetime.strptime(event_date, '%Y-%m-%d'),
            location=event_location,
            members_assigned=False
        )
        event_id = new_event.save_to_db()

        for i in members:
            new_event_mem = model.EventMembersModel(
                user_id=get_user(i),
                event_id=event_id,
                status="pending"
            )
            new_event_mem.save_to_db()

        return {'event_id': event_id, 'non-existing_users': non_existed}, 200

    def get(self):
        token = token_parser.parse_args()['token']
        cur_user = get_user_by_token(token)
        cur_user_id = get_user(cur_user.email)
        cur_user_events = []
        events = model.EventMembersModel.find_by_user(cur_user_id)
        for i in events:
            ev = model.EventsModel.find_by_id(i.event_id)
            assignee = None
            assignee_wishlist = None
            if ev.members_assigned:
                assignee = model.UserModel.find_by_id(i.asignee).email
                assignee_wishlist = model.EventMembersModel.find_by_user_event(i.asignee, i.event_id).wishlist

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
                'status': model.EventMembersModel.find_by_user_event(cur_user_id, i.event_id).status
            }
            cur_user_events.append(event)
        return cur_user_events, 200


class Invitation(Resource):

    def patch(self):
        token = token_parser.parse_args()['token']
        cur_user = get_user_by_token(token)
        cur_user_id = get_user(cur_user.email)
        invitation = invitation_parser.parse_args()
        invitation_status = invitation['status']
        event_id = invitation['event_id']
        message = model.EventMembersModel.update_status(cur_user_id, event_id, invitation_status)
        return message, 200


class Wishlist(Resource):

    def patch(self):
        token = token_parser.parse_args()['token']
        cur_user = get_user_by_token(token)
        cur_user_id = get_user(cur_user.email)
        wishlist = wishlist_parser.parse_args()
        wish = wishlist['wishlist']
        event_id = wishlist['event_id']
        message = model.EventMembersModel.update_wishlist(cur_user_id, event_id, wish)
        return message, 200


def move_left(list):
    l = list[1:]
    l.append(list[0])
    return l


class AssignGiftees(Resource):

    def patch(self):
        token = token_parser.parse_args()['token']
        cur_user = get_user_by_token(token)
        cur_user_id = get_user(cur_user.email)
        event = assignee_parser.parse_args()
        event_id = event['event_id']
        event = model.EventsModel.find_by_id(event_id)

        if event.creator != cur_user_id:
            return {'message': 'Only creator can perform this action'}, 403

        accepted = model.EventMembersModel.get_accepted_event(event_id)

        if len(accepted) <= 1:
            return {'message': 'Not enough participants'}, 406

        participants = []
        for a in accepted:
            participants.append(a.user_id)
        assignee = move_left(participants)

        model.EventsModel.update_members_assigned(event_id, True)

        for i in range(len(participants)):
            model.EventMembersModel.update_assignee(participants[i], event_id, assignee[i])

        return {'message': 'Participants assigned'}, 200
