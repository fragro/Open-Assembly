import datetime
from haystack.indexes import *
from haystack import site
from pirate_topics.models import Topic


class TopicIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Topic.objects.all()

site.register(Topic, TopicIndex)