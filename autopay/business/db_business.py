from autopay.models.db import User, Organization, Event, Tag
import json
from autopay.business.base import CrudBO
from autopay.utils import _extract_selections, now


class EventBO(CrudBO):

    model = Event
    model_selections = ['id', 'organization', 'check_in', 'check_out',
                        'user_rfid', 'cost']

    def handle_event(self, org_id, rfid, timestamp):
        """
        Method that will either checkout some checkin or
        start a new checkin
        """
        if not self.rfid_exists_in_org(rfid, org_id):
            raise ValueError("RFID user in this organization not found")

        event = self.search_open_event(org_id, rfid)

        if event is None:
            self.check_in(org_id, rfid, timestamp)
        else:
            self.check_out(event.id, org_id, rfid, timestamp)

    def rfid_exists_in_org(self, rfid, org_id):
        """
        Check if given RFID exists inside given ORG
        """
        tag_bo = TagBO()
        if tag_bo.get_tag_from_org(rfid, org_id):
            return True
        return False

    def search_open_event(self, org_id, rfid):
        """
        open event means checkin exists but
        checkout doesn't exist
        """
        query = self._session.query(self.model)\
                    .filter(self.model.organization == org_id,
                            self.model.user_rfid == rfid,
                            self.model.check_in != None,
                            self.model.check_out == None)
        obj = self.get_from(query)
        return obj

    def total_minutes(self, event_id):
        event = self.get(event_id)
        elapsed = event.check_out - event.check_in
        minutes = elapsed.seconds / 60.0
        return self.update(event_id, {'total_minutes': minutes})

    def check_in(self, org_id, rfid, check_in_time):
        event = Event(organization=org_id, user_rfid=rfid,
                      check_in=check_in_time)
        self._create(event)

    def check_out(self, event_id, org_id, rfid, check_out_time):
        success = self.update(event_id, {'check_out': check_out_time})
        self.total_minutes(event_id)
        return success

    def get_events_by_org_tag(self, org_id, tag):
        query = self._session.query(self.model)\
                    .filter(self.model.organization == org_id,
                            self.model.user_rfid == tag)
        return self._list(query=query, limit=None)


class UserBO(CrudBO):

    model = User
    model_selections = ['id', 'name', 'role']

    def create_user(self, name, pw, role=1):
        user = User(name=name, role=role)
        user.set_password(pw)

        return self._create(user, return_id=True)

    def auth_user(self, name, password):
        query = self._session.query(self.model).filter(self.model.name == name)
        user = self.get_from(query, return_obj=True)
        if not user:
            return
        if user.check_password(password):
            user_data = self.get(user.id)
            return user_data
        return

    def get_events(self, user_id):
        """
        In the future, when we have many tags for one user, we 
        will iterate through the user's tags
        """
        events = []
        event_bo = EventBO()
        tag_bo = TagBO()
        user_tags = tag_bo.get_user_tags(user_id)

        for tag in user_tags:
            events.append(event_bo.get_events_by_org_tag(tag['organization'],
                                                         tag['tag']))
        # flat list
        events = [event for sublist in events for event in sublist]
        return events


class OrganizationBO(CrudBO):

    model = Organization
    model_selections = ['id', 'name', 'password']

    def create_org(self, name, pw):
        org = Organization(name=name)
        org.set_password(pw)

        return self._create(org, return_id=True)

    def auth_organization(self, id, password):
        org = self.get(id, return_obj=True)
        if org.check_password(password):
            return True
        return False


class TagBO(CrudBO):

    model = Tag
    model_selections = ['id', 'user', 'organization', 'tag']

    def get_user_tags(self, user_id):
        query = self._session.query(self.model)\
                             .filter(self.model.user == user_id)
        return self._list(query=query, limit=None)

    def get_tag_from_org(self, tag, org_id):
        query = self._session.query(self.model)\
                    .filter(self.model.organization == org_id,
                            self.model.tag == tag)
        
        obj = self.get_from(query)
        return obj

    def create_tag(self, user_id, org_id, tag):
        tag = Tag(user=user_id, organization=org_id, tag=tag)
        return self._create(tag, return_id=True)
