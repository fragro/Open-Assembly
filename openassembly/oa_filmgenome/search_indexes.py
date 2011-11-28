import search
from search.core import startswith, porter_stemmer
from oa_filmgenome.models import Film, FilmIdea, Scene

search.register(FilmIdea, ('summary','description'), search_index='autocomplete_index',indexer=startswith)
search.register(FilmIdea, ('summary','description'), search_index='search_index',indexer=porter_stemmer)

