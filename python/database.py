import sqlite3
import DAD_Utils
import logging
import sqlite3

logger = logging.getLogger()  # Get the root logger configured in main.py

# Insert item into the database
def insertItem(cursor,values):
    sql = """
        INSERT INTO items (name, rarity, rolls, price, goodRoll)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(sql,values)

def getStoredItems(cursor):
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(row)
    else: logger.debug("empty database")
    return rows


def closeDatabase(conn):
    conn.commit()
    conn.close()


# Define the database connection
def connectDatabase():
    # Connect to the database 
    logger.debug("Connecting to database...")
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    # Create the items table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Items (
        name TEXT,
        rarity TEXT,
        rolls TEXT,
        price INTEGER,
        goodRoll INTEGER
    );
    """)

    return conn, cursor