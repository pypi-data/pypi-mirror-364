# coffy/sql/engine.py
# author: nsarathy

import sqlite3
from .sqldict import SQLDict

# Internal connection state
_connection = None
_cursor = None

def initialize(db_path=None):
    """Initialize the database connection."""
    global _connection, _cursor
    if _connection:
        return  # already initialized
    _connection = sqlite3.connect(db_path or ":memory:") # Uses in-memory DB if no path provided
    _cursor = _connection.cursor()

def execute_query(sql: str):
    if _connection is None:
        initialize()  # uses in-memory if not initialized

    try:
        _cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            columns = [desc[0] for desc in _cursor.description]
            rows = _cursor.fetchall()
            return SQLDict([dict(zip(columns, row)) for row in rows])
        else:
            _connection.commit()
            return {"status": "success", "rows_affected": _cursor.rowcount}
    except Exception as e:
        return {"status": "error", "message": str(e)}
