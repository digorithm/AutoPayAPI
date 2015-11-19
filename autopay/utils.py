# -*- encoding: utf-8 -*-
import time
import datetime

selections_names = {}


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def _extract_selections(obj, selections):

    if isinstance(obj, list):
        items = []
        for item in obj:
            items.append(_extract_item_selections(item, selections))
        return items
    return _extract_item_selections(obj, selections)


def _extract_item_selections(obj, selections):
    """
      Maps a obj into a dict, for the giving selections
    """

    if obj is None:
      return None

    if not isinstance(obj, dict):
        obj = _extract_properties_atributes(obj)

    item = {}
    for selection in selections:
        if isinstance(selection, dict):
            subselection, subselections = selection.items()[0]
            subobj = _extract_selections(obj.get(subselection), subselections)
            item[selections_names.get(subselection, subselection)] = subobj
        else:
            item[selections_names.get(selection, selection)] = obj.get(selection)
    # Make it accessible via ['attr'] and .attr
    return AttrDict(item)


def _extract_properties_atributes(obj):
    properties_atributes = {}

    for properties_atribute in dir(obj):
        properties_atributes[properties_atribute] = getattr(obj,properties_atribute)

    return properties_atributes


def now():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st
