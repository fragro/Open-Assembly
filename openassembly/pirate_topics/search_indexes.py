import search
from search.core import startswith, porter_stemmer
from models import Topic

search.register(Topic, ('summary', 'description'), search_index='autocomplete_index', indexer=startswith)
search.register(Topic, ('summary', 'description'), search_index='search_index',  indexer=porter_stemmer)
