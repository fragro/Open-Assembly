import search
from search.core import startswith, porter_stemmer
from models import Problem, Solution, Policy

search.register(Problem, ('summary','description'), search_index='search_index',indexer=porter_stemmer)

search.register(Solution, ('summary','description'), search_index='search_index',indexer=porter_stemmer)

search.register(Policy, ('summary','description'), search_index='search_index',indexer=porter_stemmer)
