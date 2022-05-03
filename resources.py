from datetime import datetime

import firebase_admin
import sqlalchemy
from firebase_admin import auth, credentials
from flask_restful import Resource, reqparse, abort

import model
from app import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

token_parser = reqparse.RequestParser()
token_parser.add_argument('token', help='This field cannot be blank', required=True, location='headers')

event_parser = reqparse.RequestParser()
event_parser.add_argument('name', help='This field cannot be blank', required=True, location='json')
event_parser.add_argument('gift_date', help='This field cannot be blank', required=True, location='json')
event_parser.add_argument('location', help='This field cannot be blank', required=True, location='json')
event_parser.add_argument('members', help='This field cannot be blank', required=True, action='append', location='json')

invitation_parser = reqparse.RequestParser()
invitation_parser.add_argument('status', help='This field cannot be blank', required=True, location='args')
invitation_parser.add_argument('event_id', help='This field cannot be blank', required=True, location='args')

wishlist_parser = reqparse.RequestParser()
wishlist_parser.add_argument('event_id', help='This field cannot be blank', required=True, location='args')
wishlist_parser.add_argument('wishlist', help='This field cannot be blank', required=True, location='args')

assignee_parser = reqparse.RequestParser()
assignee_parser.add_argument('event_id', help='This field cannot be blank', required=True, location='args')


def authenticate_user(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        firebase_user = auth.get_user(uid)
    except auth.InvalidIdTokenError:
        raise abort(401, message="Invalid Firebase ID Token")
    except auth.UserNotFoundError:
        raise abort(401, message="User not found by Firebase UID")

    return model.User.get_or_create(firebase_user.email)


# check if user exist in database
def check_user(user_email):
    if model.User.find_by_email(user_email) is None:
        return False
    return True


# noinspection PyMethodMayBeStatic
class Event(Resource):

    def post(self):

        token = token_parser.parse_args()['token']
        user = authenticate_user(token)

        event = event_parser.parse_args()
        event_name = event['name']
        event_date = event['gift_date']
        event_location = event['location']
        event_members = set(event['members'])

        if len(event_members) < 1:
            raise abort(400, message="At least 1 member of event is required")

        if len(event_members) > 10:
            raise abort(400, message="Maximum 10 members allowed")

        members = model.User.ensure_all_users_exist(event_members)
        new_event = model.Event.create_with_memberships(
            creator_id=user.id,
            name=event_name,
            gift_date=datetime.strptime(event_date, '%Y-%m-%d'),
            location=event_location,
            members=members
        )
        return {'id': new_event.id, 'name': new_event.name}, 200

    def get(self):
        token = token_parser.parse_args()['token']
        user = authenticate_user(token)
        cur_user_events = []
        try:
            memberships = model.Membership.find_by_user(user.id)
        except (sqlalchemy.exc.InterfaceError, AttributeError):
            return {'message': 'Wrong database request, could not find event'}, 500

        for membership in memberships:
            try:
                event = model.Event.find_by_id(membership.event_id)
            except (sqlalchemy.exc.InterfaceError, AttributeError):
                return {'message': 'Wrong database request, could not find event'}, 500

            assignee = None
            assignee_wishlist = None
            if event.members_assigned:
                try:
                    assignee = model.User.find_by_id(membership.asignee).email
                    assignee_wishlist = model.Membership.find_by_user_event(membership.asignee, membership.event_id).wishlist
                except (sqlalchemy.exc.InterfaceError, AttributeError):
                    return {'message': 'Wrong database request, could not find assignee or wishlist'}, 500

            cur_user_events.append({
                'event_id': membership.event_id,
                'invitations': event.members,
                'accepted_members': len(model.Membership.get_accepted_event(membership.event_id)),
                'creator': model.User.find_by_id(event.creator).email,
                'name': event.name,
                'gift_date': str(event.gift_date),
                'location': event.location,
                'current_user_wishlist': membership.wishlist,
                'members_assigned': event.members_assigned,
                'assignee_email': assignee,
                'assignee_wishlist': assignee_wishlist,
                'status': model.Membership.find_by_user_event(user.id, membership.event_id).status
            })

        return cur_user_events, 200


class Invitation(Resource):

    def patch(self):
        token = token_parser.parse_args()['token']
        user = authenticate_user(token)

        try:
            invitation = invitation_parser.parse_args()
            invitation_status = invitation['status']
            event_id = invitation['event_id']
        except:
            return {'message': 'Wrong request arguments'}, 400

        if invitation_status not in ['accepted', 'pending', 'denied']:
            return {'message': 'Wrong status: it should be "accepted", "pending" or "denied"'}, 400

        try:
            message = model.Membership.update_status(user.id, event_id, invitation_status)
        except Exception as e:
            return {'message': str(e)}, 500

        return message, 200


class Wishlist(Resource):

    def patch(self):
        token = token_parser.parse_args()['token']
        user = authenticate_user(token)

        try:
            wishlist = wishlist_parser.parse_args()
            wish = wishlist['wishlist']
            event_id = wishlist['event_id']
        except:
            return {'message': 'Wrong request arguments'}, 400

        try:
            message = model.Membership.update_wishlist(user.id, event_id, wish)
        except Exception as e:
            return {'message': str(e)}, 500

        return message, 200


def move_left(list):
    l = list[1:]
    l.append(list[0])
    return l


class AssignGiftees(Resource):

    def patch(self):
        token = token_parser.parse_args()['token']
        event = assignee_parser.parse_args()
        event_id = event['event_id']

        user = authenticate_user(token)

        try:
            event = model.Event.find_by_id(event_id)
        except (sqlalchemy.exc.InterfaceError, AttributeError):
            return {'message': 'Wrong database request, could not find model'}, 500

        if event is None:
            return {'message': 'No events found'}, 500

        if event.creator != user.id:
            return {'message': 'Only creator can perform this action'}, 403

        try:
            accepted = model.Membership.get_accepted_event(event_id)
        except (sqlalchemy.exc.InterfaceError, AttributeError):
            return {'message': 'Wrong database request, could not find accepted events'}, 500

        if len(accepted) <= 1:
            return {'message': 'Not enough participants'}, 406

        participants = []
        for a in accepted:
            participants.append(a.user_id)
        assignee = move_left(participants)

        try:
            model.Event.update_members_assigned(event_id, True)
            db.session.flush()
        except Exception as e:
            return {'message': str(e)}, 500

        for i in range(len(participants)):
            try:
                model.Membership.update_assignee(participants[i], event_id, assignee[i])
                db.session.flush()
            except Exception as e:
                return {'message': str(e)}, 500

        try:
            db.session.commit()
        except Exception as e:
            return {'message': str(e)}, 500

        return {'message': 'Participants assigned'}, 200