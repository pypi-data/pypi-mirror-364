# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    PLONE_FIXTURE,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    applyProfile,
)
from plone.testing import z2

import collective.volto.slotseditor


class VoltoSlotsEditorLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity

        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=collective.volto.slotseditor)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.volto.slotseditor:default")


FIXTURE = VoltoSlotsEditorLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="VoltoSlotsEditorLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name="VoltoSlotsEditorLayer:FunctionalTesting",
)


ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="VoltoSlotsEditorLayer:AcceptanceTesting",
)
