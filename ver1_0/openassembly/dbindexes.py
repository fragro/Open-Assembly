from dbindexer.api import register_index
from pirate_forum.models import View
# dbindexes.py:
register_index(View, {'modified_dt': 'month', 'modified_dt': 'day',
						'modified_dt': 'year', 'created_dt': 'month', 'created_dt': 'day', 'created_dt': 'year'})
