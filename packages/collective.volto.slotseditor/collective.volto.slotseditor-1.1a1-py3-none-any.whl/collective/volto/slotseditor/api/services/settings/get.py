# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.i18n import translate
from zope.interface import Interface, implementer
from zope.schema import getFields

from collective.volto.slotseditor.api.serializers.slotseditor_settings import (
    serialize_data,
)
from collective.volto.slotseditor.controlpanels import (
    ICollectiveVoltoSlotsEditorControlPanel,
)


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class VoltoSlotsEditorSettings(object):
    def __init__(self, context, request):
        self.context = context.aq_explicit
        self.request = request

    def __call__(self, expand=False):
        # import pdb

        # pdb.set_trace()
        # TODO: Handle expand

        # Using the fieldset key to ensure that the removed fields from ISocialMediaSchema aren't included
        fields = [field for field in getFields(ICollectiveVoltoSlotsEditorControlPanel)]
        records = {}

        try:
            records = {
                field: api.portal.get_registry_record(
                    # TODO: Why do I need to manually add the prefix here and why does using the `interface` argument fail?
                    f"collective.volto.slotseditor.slotseditor_control_panel.{field}",
                    default="",
                )
                for field in fields
            }
        except KeyError:
            # TODO: Better logging & response of missing key
            return {}
        except Exception as e:
            # TODO: Do I need a 400 error?
            self.request.response.setStatus(400)
            return {
                "error": dict(
                    type=e.__class__.__name__,
                    message=translate(str(e), context=self.request),
                )
            }

        if not records:
            return {}

        return serialize_data(records)


class VoltoSlotsEditorSettingsGet(Service):
    def reply(self):
        service_factory = VoltoSlotsEditorSettings(self.context, self.request)
        # TODO: Handle expand
        return service_factory(expand=True)
