from autopay import db
from autopay.utils import _extract_selections

# IMPORTANT: db.engine.dispose is being tested
# if something is wrong, undo that

class BaseBO(object):

    def __init__(self, session=None):
        self._session = db.session()


class CrudBO(BaseBO):

    def list(self, limit=50):
        return self._list(limit=limit)

    def _list(self, model=None, selections=None, limit=50, query=None):
        model = model or self.model
        selections = selections or self.model_selections

        if query is None:
            query = self._session.query(model)

        if limit is not None:
            query = query.limit(limit)

        try:
            objects = query.all()
            return _extract_selections(objects, selections)
        finally:
            self._session.close()
            db.engine.dispose()

    def get(self, id, return_obj=False):
        try:
            obj = self._session.query(self.model).filter(self.model.id == id)\
                                                 .first()
            if not return_obj:
                return _extract_selections(obj, self.model_selections)
            return obj
        finally:
            self._session.close()
            db.engine.dispose()

    def get_from(self, query, selections=None, return_obj=False):
        """
          Returns a object filtered by a query
        """
        selections = selections or self.model_selections
        try:
            obj = query.first()
            if not return_obj:
                return _extract_selections(obj, selections)
            return obj
        finally:
            self._session.close()
            db.engine.dispose()

    def _create(self, obj, return_id=False):

        try:
            self._session.add(obj)
            self._session.commit()

        except Exception as e:
            raise e

        finally:
            if return_id:
                return obj.id
            self._session.close()
            db.engine.dispose()

    def update(self, id, changes):
        success = True
        try:
            self._session.query(self.model) \
                .filter(self.model.id == id) \
                .update(changes)
            self._session.commit()
        except Exception as e:
            logger.exception(e)
            success = False
        finally:
            self._session.close()
            db.engine.dispose()
        return success

    def update_many(self, ids, changes):
        for _id in ids:
            self.update(_id, changes)

    def get_many(self, ids):
        """
            Receives a list of ids and returns a map where the keys are the ids
            and the values are the retrieved objects.
        """
        objects = self._session.query(self.model).filter(self.model.id.in_(ids)).all()
        return {obj.id: _extract_selections(obj, self.model_selections) for obj in objects}
