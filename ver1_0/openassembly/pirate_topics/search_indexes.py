import search
from search.core import startswith, porter_stemmer
from models import Topic
from django.contrib.auth.models import User

search.register(Topic, ('summary', 'description'), search_index='autocomplete_index', indexer=startswith)
search.register(Topic, ('summary', 'description'), search_index='search_index',  indexer=porter_stemmer)

#lets also add users for searching here
search.register(User, ('username'), search_index='search_index',  indexer=porter_stemmer)