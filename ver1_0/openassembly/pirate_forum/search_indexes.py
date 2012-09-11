import datetime
from haystack.indexes import *
from haystack import site
from pirate_forum.models import Question


class QuestionIndex(SearchIndex):
    text = CharField(document=True, use_template=True)

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return Question.objects.all()

site.register(Question, QuestionIndex)