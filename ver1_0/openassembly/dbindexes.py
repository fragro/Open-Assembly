from dbindexer.api import register_index
from tagging.models import Tag

register_index(MyModel, {'name': 'icontains'})
