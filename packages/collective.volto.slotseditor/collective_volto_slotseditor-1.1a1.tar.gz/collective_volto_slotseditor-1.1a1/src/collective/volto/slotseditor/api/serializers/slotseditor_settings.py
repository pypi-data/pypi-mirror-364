# -*- coding: utf-8 -*-
import json

from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.controlpanels import ControlpanelSerializeToJson
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.interface import implementer

from collective.volto.slotseditor.controlpanels.slotseditor.controlpanel import ICollectiveVoltoSlotsEditorControlPanel

KEYS_WITH_URL = ["linkUrl", "navigationRoot", "showMoreLink"]


def serialize_data(json_data):
    if not json_data:
        return ""

    return json_compatible(json_data)


@implementer(ISerializeToJson)
@adapter(ICollectiveVoltoSlotsEditorControlPanel)
class VoltoSlotsEditorControlpanelSerializeToJson(ControlpanelSerializeToJson):
    def __call__(self):
        json_data = super(VoltoSlotsEditorControlpanelSerializeToJson, self).__call__()
        conf = json_data["data"].get("volto_slots_editor_controlpanel_data", "")
        if conf:
            json_data["data"]["volto_slots_editor_controlpanel_data"] = json.dumps(
                serialize_data(json_data=conf)
            )
        return json_data
