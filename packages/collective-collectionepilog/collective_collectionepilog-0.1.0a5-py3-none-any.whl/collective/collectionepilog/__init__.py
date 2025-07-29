"""Init and utils."""

import logging
from zope.i18nmessageid import MessageFactory

__version__ = "0.1.0a5"

PACKAGE_NAME = "collective.collectionepilog"

_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)
