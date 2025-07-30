# -*- coding: utf-8 -*-
import json

from plone.app.registry.browser.controlpanel import (
    ControlPanelFormWrapper,
    RegistryEditForm,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from plone.schema import JSONField
from zope import schema
from zope.component import adapter
from zope.interface import Interface

from collective.volto.slotseditor import _
from collective.volto.slotseditor.interfaces import ICollectiveVoltoSlotsEditorLayer

title = "Slots editor"


class ICollectiveVoltoSlotsEditorControlPanel(Interface):
    volto_slots_editor_controlpanel_data = JSONField(
        title=_("volto_slots_editor_controlpanel_data_label", default="Slots"),
        description="",
        required=True,
        default={},
    )


class CollectiveVoltoSlotsEditorControlPanel(RegistryEditForm):
    schema = ICollectiveVoltoSlotsEditorControlPanel
    schema_prefix = "collective.volto.slotseditor.slotseditor_control_panel"
    label = _(title)


CollectiveVoltoSlotsEditorControlPanelView = layout.wrap_form(
    CollectiveVoltoSlotsEditorControlPanel, ControlPanelFormWrapper
)


@adapter(Interface, ICollectiveVoltoSlotsEditorLayer)
class CollectiveVoltoSlotsEditorControlPanelConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = ICollectiveVoltoSlotsEditorControlPanel
    configlet_id = "slotseditor-controlpanel"
    configlet_category_id = "Products"
    title = _(title)
    group = ""
    schema_prefix = "collective.volto.slotseditor.slotseditor_control_panel"
