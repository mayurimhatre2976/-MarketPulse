import os
import pymysql
import pymysql.cursors
import sqlite3
from contextlib import contextmanager
from config import Config

# Track if we are in MySQL mode or SQLite fallback mode
_USE_SQLITE = False
_SQLITE_PATH = os.path.join(os.path.dirname(__file__), 'marketpulse.sqlite3')

def is_mysql_available():
    """Check if MySQL server is reachable with configured credentials."""
    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception:
        return False

def get_connection():
    """
    Returns an active database connection.
    Defaults to PyMySQL (XAMPP MySQL). If MySQL is offline, smoothly uses SQLite fallback.
    """
    global _USE_SQLITE
    if not _USE_SQLITE:
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                charset='utf8mb4'
            )
            return conn
        except Exception:
            # Fallback to SQLite if MySQL cannot be reached
            _USE_SQLITE = True

    # SQLite fallback
    conn = sqlite3.connect(_SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class DBWrapper:
    """Unified wrapper supporting both PyMySQL DictCursor and SQLite Row cursors."""
    def __init__(self, conn):
        self.conn = conn
        self.is_sqlite = isinstance(conn, sqlite3.Connection)
        self.cursor = conn.cursor()

    def execute(self, sql, params=()):
        # SQLite uses '?' while PyMySQL uses '%s'
        if self.is_sqlite:
            # Replace MySQL specific syntax and placeholders
            sqlite_sql = sql.replace('%s', '?')
            # Normalize MySQL NOW() - INTERVAL X DAY to SQLite datetime('now', '-X day')
            # and CURDATE() to date('now')
            sqlite_sql = sqlite_sql.replace('NOW()', "datetime('now', 'localtime')")
            sqlite_sql = sqlite_sql.replace('CURDATE()', "date('now', 'localtime')")
            self.cursor.execute(sqlite_sql, params)
        else:
            self.cursor.execute(sql, params)
        return self.cursor

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        if self.is_sqlite:
            return dict(row)
        return row

    def fetchall(self):
        rows = self.cursor.fetchall()
        if self.is_sqlite:
            return [dict(r) for r in rows]
        return rows

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass

@contextmanager
def get_db():
    """Context manager for obtaining a managed database connection and cursor."""
    conn = get_connection()
    wrapper = DBWrapper(conn)
    try:
        yield wrapper
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        wrapper.close()
        conn.close()

def query_db(query, args=(), one=False):
    """Convenience helper to run a SELECT query and fetch results."""
    with get_db() as db:
        db.execute(query, args)
        return db.fetchone() if one else db.fetchall()

def execute_db(query, args=()):
    """Convenience helper to run INSERT/UPDATE/DELETE and return lastrowid and rowcount."""
    with get_db() as db:
        db.execute(query, args)
        return {
            'lastrowid': db.lastrowid,
            'rowcount': db.rowcount
        }

def init_database_tables():
    """Initializes the database schema."""
    global _USE_SQLITE
    if is_mysql_available():
        # Connect without database first to ensure marketpulse database exists
        try:
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Warning creating MySQL database: {e}")

        # Execute schema.sql statements
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME
            )
            with conn.cursor() as cur:
                for stmt in statements:
                    if stmt:
                        try:
                            cur.execute(stmt)
                        except Exception as ex:
                            print(f"Schema execution note: {ex}")
            conn.commit()
            conn.close()
            print("MySQL database and tables successfully initialized.")
            _USE_SQLITE = False
            return True
    
    # SQLite initialization fallback
    _USE_SQLITE = True
    conn = sqlite3.connect(_SQLITE_PATH)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'customer',
        points_balance INTEGER NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS rewards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        required_points INTEGER NOT NULL,
        reward_value REAL NOT NULL DEFAULT 0.00,
        stock INTEGER NOT NULL DEFAULT 0,
        expiry_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT,
        discount_type TEXT NOT NULL DEFAULT 'fixed',
        discount_value REAL NOT NULL DEFAULT 0.00,
        minimum_purchase REAL NOT NULL DEFAULT 0.00,
        maximum_usage INTEGER NOT NULL DEFAULT 100,
        used_count INTEGER NOT NULL DEFAULT 0,
        start_date TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    );

    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        invoice_number TEXT NOT NULL UNIQUE,
        amount REAL NOT NULL,
        discount_amount REAL NOT NULL DEFAULT 0.00,
        final_amount REAL NOT NULL,
        coupon_id INTEGER NULL,
        description TEXT,
        purchase_date TEXT NOT NULL,
        points_earned INTEGER NOT NULL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (customer_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (coupon_id) REFERENCES coupons (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS loyalty_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        purchase_id INTEGER NULL,
        transaction_type TEXT NOT NULL,
        points INTEGER NOT NULL,
        description TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (customer_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (purchase_id) REFERENCES purchases (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS reward_redemptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        reward_id INTEGER NOT NULL,
        points_used INTEGER NOT NULL,
        redemption_code TEXT NOT NULL UNIQUE,
        redemption_date TEXT DEFAULT (datetime('now', 'localtime')),
        status TEXT NOT NULL DEFAULT 'completed',
        FOREIGN KEY (customer_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (reward_id) REFERENCES rewards (id) ON DELETE RESTRICT
    );

    CREATE TABLE IF NOT EXISTS coupon_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coupon_id INTEGER NOT NULL,
        customer_id INTEGER NOT NULL,
        purchase_id INTEGER NULL,
        discount_applied REAL NOT NULL DEFAULT 0.00,
        used_at TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY (coupon_id) REFERENCES coupons (id) ON DELETE CASCADE,
        FOREIGN KEY (customer_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (purchase_id) REFERENCES purchases (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        campaign_type TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        target_audience TEXT NOT NULL DEFAULT 'All Customers',
        offer TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    );
    """)
    conn.commit()
    conn.close()
    print("Database tables initialized successfully (SQLite mode).")
    return True
