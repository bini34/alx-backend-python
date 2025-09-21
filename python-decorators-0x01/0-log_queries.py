import sqlite3
import functools

def log_queries():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            query = kwargs.get('query')
            if query:
                print(f"Executing SQL Query: {query}")
            elif args:
                # Try to find query in positional args
                for arg in args:
                    if isinstance(arg, str) and arg.strip().lower().startswith('select'):
                        print(f"Executing SQL Query: {arg}")
                        break
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log_queries()
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
