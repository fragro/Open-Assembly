import search
from search.core import startswith, porter_stemmer
from models import Question, Nomination

search.register(Question, ('summary', 'description'), search_index='autocomplete_index', indexer=startswith)
search.register(Question, ('summary', 'description'), search_index='search_index',  indexer=porter_stemmer)

search.register(Nomination, ('summary', 'description'), search_index='autocomplete_index', indexer=startswith)
search.register(Nomination, ('summary', 'description'), search_index='search_index',  indexer=porter_stemmer)
