# -*- coding: utf-8 -*-
from collective.collectionepilog.behaviors.collection_epilog import ICollectionEpilogMarker
from collective.collectionepilog.testing import COLLECTIVE_COLLECTIONEPILOG_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class CollectionEpilogIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_COLLECTIONEPILOG_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_collection_epilog(self):
        behavior = getUtility(IBehavior, 'collective.collectionepilog.collection_epilog')
        self.assertEqual(
            behavior.marker,
            ICollectionEpilogMarker,
        )
