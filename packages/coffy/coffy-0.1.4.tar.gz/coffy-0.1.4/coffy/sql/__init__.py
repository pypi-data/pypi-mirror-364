# coffy/sql/__init__.py
# author: nsarathy

from .engine import execute_query, initialize

def init(path: str = None):
    initialize(path)

def query(sql: str):
    return execute_query(sql)
