"""
Database connection pool for SAI PRAVESH (Flask version).
Equivalent to the old db.js (mysql2 pool).
"""

import os
from mysql.connector import pooling, Error as MySQLError

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_NAME = os.getenv("DB_NAME", "saipravesh")

pool = None


def init_pool():
    global pool
    if pool is not None:
        return pool
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="sai_pravesh_pool",
            pool_size=10,
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
        )
        test_conn = pool.get_connection()
        print("✅ MySQL connected successfully")
        test_conn.close()
    except MySQLError as err:
        pool = None
        print(f"❌ Database connection failed: {err}")
    return pool


# Try initializing pool on module load
init_pool()


def get_connection():
    """Grab a connection from the pool. Re-initializes pool if necessary."""
    global pool
    if pool is None:
        init_pool()
    if pool is None:
        raise MySQLError("Database pool not initialized. Check your database credentials and availability.")
    return pool.get_connection()


def query(sql, params=None, fetch=True, dict_cursor=True):
    """
    Run a query and return rows (for SELECT) or the connection's cursor
    info (lastrowid, rowcount) for INSERT/UPDATE.

    fetch=True  -> returns list of dict rows
    fetch=False -> returns (lastrowid, rowcount) after commit, for writes
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=dict_cursor)
        cursor.execute(sql, params or ())

        if fetch:
            rows = cursor.fetchall()
            cursor.close()
            return rows
        else:
            conn.commit()
            result = (cursor.lastrowid, cursor.rowcount)
            cursor.close()
            return result
    finally:
        conn.close()