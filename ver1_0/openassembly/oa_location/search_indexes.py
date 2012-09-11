import datetime
from haystack.indexes import *
from haystack import site
from oa_location.models import Place


class PlaceIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Place.objects.all()

site.register(Place, PlaceIndex)