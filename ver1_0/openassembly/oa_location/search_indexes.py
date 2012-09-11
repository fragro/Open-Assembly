import datetime
from haystack.indexes import *
from haystack import site
from oa_location.models import Location


class LocationIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Location.objects.all()

site.register(Location, LocationIndex)