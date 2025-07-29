from Acquisition import aq_base
from plone.app.layout.viewlets import ViewletBase


class CollectionEpilog(ViewletBase):

    def update(self):
        self.epilog = self._epilog()

    def get_message(self):
        return u'My message'

    def index(self):
        return super(CollectionEpilog, self).render()

    def _epilog(self):
        textfield = getattr(aq_base(self.context), "epilog", None)
        epilog = (
            textfield.output_relative_to(self.context)
            if getattr(textfield, "output_relative_to", None)
            else None
        )
        if epilog:
            self.epilog_class = (
                "stx"
                if textfield.mimeType
                in ("text/structured", "text/x-rst", "text/restructured")
                else "plain"
            )
        return epilog