import json
from autopay import app 
from flask_restful import Resource, Api, reqparse, abort
from flask import request, g, jsonify
from autopay.business.db_business import EventBO, OrganizationBO, UserBO

api = Api(app)

parser = reqparse.RequestParser()

event_bo = EventBO()
org_bo = OrganizationBO()
user_bo = UserBO()


class Event(Resource):

    parser.add_argument('rfid', type=str)
    parser.add_argument('org_id', type=str)
    parser.add_argument('timestamp', type=str)

    def post(self):

        args = parser.parse_args()
        rfid = args['rfid']
        timestamp = args['timestamp']
        org_id = args['org_id']
        print "### receiving event ###"
        print "tag: ", rfid
        print "time: ", timestamp
        try:
            event_bo.handle_event(org_id, rfid, timestamp)
        except:
            abort(500, message="Something went wrong")
        finally:
            return "Event processed correctly", 200


class OrganizationAuth(Resource):

    parser.add_argument('password', type=str)
    parser.add_argument('org_id', type=str)

    def get(self):
        args = parser.parse_args()
        org_id = int(args['org_id'])
        password = args['password']

        if org_bo.auth_organization(org_id, password):
            return "true", 201
        return "false", 402


class UserAuth(Resource):

    parser.add_argument('username', type=str)
    parser.add_argument('password', type=str)

    def get(self):

        args = parser.parse_args()
        password = args['password']
        username = args['username']

        user = user_bo.auth_user(username, password)

        if user is None:
            return "Username or password incorrect", 402
        else:

            return user, 201


class User(Resource):

    parser.add_argument('user_id', type=str)

    def get(self):

        args = parser.parse_args()
        id = args['user_id']
        user = user_bo.get(int(id))

        return user

api.add_resource(Event, '/api/v1/event')
api.add_resource(OrganizationAuth, '/api/v1/organizationauth')
api.add_resource(UserAuth, '/api/v1/userauth')
api.add_resource(User, '/api/v1/user')
