from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import queryUtility
from plone.api.portal import get_registry_record, set_registry_record

import logging
import json


logger = logging.getLogger(__name__)

REGISTRY_RECORD_ID = "collective.volto.slotseditor.slotseditor_control_panel.volto_slots_editor_controlpanel_data"


def update_controlpanel_value_type(setup_context):
    """Rename iface name to the short name in blocks"""
    value = get_registry_record(REGISTRY_RECORD_ID)

    if isinstance(value, str):
        logger.info(f"Slots editor upgrade: Registry value is string. Updating value: {value}")
        try:
            converted_value = json.loads
        except AttributeError as e:
            logger.info(f"Slots editor upgrade: JSON FAILURE")
            raise e
        except json.JSONDecodeError as e:
            logger.info(f"Slots editor upgrade: JSON FAILURE")
            raise e

        set_registry_record(REGISTRY_RECORD_ID, converted_value)

        logger.info(f"Slots editor upgrade: Registry value converted to dictionary. Finishing upgrade.")
    else:
        logger.info("Slots editor: Registry value is already object type. Finishing upgrade.")
