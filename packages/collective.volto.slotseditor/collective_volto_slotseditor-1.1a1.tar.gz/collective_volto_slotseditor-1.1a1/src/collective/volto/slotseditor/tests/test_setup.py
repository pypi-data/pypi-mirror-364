# -*- coding: utf-8 -*-
"""Setup tests for this package."""
# noqa: E501
import unittest

from plone import api
from plone.app.testing import TEST_USER_ID, setRoles

from collective.volto.slotseditor.testing import (
    INTEGRATION_TESTING,
)

try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that collective.volto.slotseditor is properly installed."""

    layer = INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if collective.volto.slotseditor is installed."""
        self.assertTrue(
            self.installer.is_product_installed("collective.volto.slotseditor")
        )

    def test_browserlayer(self):
        """Test that ICollectiveVoltoSlotsEditorLayer is registered."""
        from plone.browserlayer import utils

        from collective.volto.slotseditor.interfaces import (
            ICollectiveVoltoSlotsEditorLayer,
        )

        self.assertIn(ICollectiveVoltoSlotsEditorLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("collective.volto.slotseditor")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.volto.slotseditor is cleanly uninstalled."""
        self.assertFalse(
            self.installer.is_product_installed("collective.volto.slotseditor")
        )

    def test_browserlayer_removed(self):
        """Test that ICollectiveVoltoSlotsEditorLayer is removed."""
        from plone.browserlayer import utils

        from collective.volto.slotseditor.interfaces import (
            ICollectiveVoltoSlotsEditorLayer,
        )

        self.assertNotIn(ICollectiveVoltoSlotsEditorLayer, utils.registered_layers())
