import time
import sqlite3 
import functools

query_cache = {}

def cache_query(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the query from either kwargs or args
        query = kwargs.get('query', args[1] if len(args) > 1 else None)
        
        # If query is in cache, return cached result
        if query in query_cache:
            print("Using cached result for query:", query)
            return query_cache[query]
        
        # If not in cache, execute query and cache the result
        result = func(*args, **kwargs)
        query_cache[query] = result
        print("Caching result for query:", query)
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users") 