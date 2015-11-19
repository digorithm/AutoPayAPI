import json
from autopay import app 
from flask_restful import Resource, Api, reqparse, abort
from flask import request, g, jsonify
from autopay.business.db_business import EventBO, OrganizationBO, UserBO, TagBO

api = Api(app)

parser = reqparse.RequestParser()

event_bo = EventBO()
org_bo = OrganizationBO()
user_bo = UserBO()


class Event(Resource):

    parser.add_argument('rfid', type=str)
    parser.add_argument('org_id', type=str)
    parser.add_argument('timestamp', type=str)
    parser.add_argument('user_id', type=str)

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

    def get(self):

        args = parser.parse_args()
        user_id = args['user_id']

        events = user_bo.get_events(user_id)

        for event in events:
            org_id = event['organization']
            org_name = org_bo.get(int(org_id))['name']
            event['organization'] = org_name
            
            if event['check_out'] is not None:
                event['horario'] = str(event['check_in'].hour)\
                    + ":" + str(event['check_in'].minute)\
                    + " / " + str(event['check_out'].hour)\
                    + ":" + str(event['check_out'].minute)
            else:
                event['horario'] = str(event['check_in'].hour)\
                    + ":" + str(event['check_in'].minute)\
                    + " / "

            event['date'] = str(event['check_in'].day)\
                + "/" + str(event['check_in'].month)\
                + "/" + str(event['check_in'].year)
            del event['check_in']
            del event['check_out']

        return events


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


class Tag(Resource):

    parser.add_argument('user_id', type=str)
    parser.add_argument('org_id', type=str)
    parser.add_argument('tag', type=str)

    def get(self):

        args = parser.parse_args()
        user_id = args['user_id']
        tag_bo = TagBO()
        org_bo = OrganizationBO()
        tags = tag_bo.get_user_tags(user_id)
        for tag in tags:
            tag['org_name'] = org_bo.get(tag['organization'])['name']

        return tags

    def post(self):
        args = parser.parse_args()
        user_id = args['user_id']
        org_id = args['org_id']
        tag = args['tag']
        tag_bo = TagBO()
        return tag_bo.create_tag(user_id, org_id, tag)


api.add_resource(Event, '/api/v1/event')
api.add_resource(OrganizationAuth, '/api/v1/organizationauth')
api.add_resource(UserAuth, '/api/v1/userauth')
api.add_resource(User, '/api/v1/user')
api.add_resource(Tag, '/api/v1/tag')
