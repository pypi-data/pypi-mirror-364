from collective.collectionepilog import _
from plone.app.textfield import RichText
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.CMFPlone.utils import safe_hasattr
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class ICollectionEpilogMarker(Interface):
    pass


@provider(IFormFieldProvider)
class ICollectionEpilog(model.Schema):
    """ """

    epilog = RichText(
        title=_(
            "Epilog",
        ),
        description=_(
            "",
        ),
        default="",
        required=False,
        readonly=False,
    )


@implementer(ICollectionEpilog)
@adapter(ICollectionEpilogMarker)
class CollectionEpilog(object):
    def __init__(self, context):
        self.context = context

    @property
    def epilog(self):
        if safe_hasattr(self.context, "epilog"):
            return self.context.epilog
        return None

    @epilog.setter
    def epilog(self, value):
        self.context.epilog = value
