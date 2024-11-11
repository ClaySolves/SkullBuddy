import sqlite3
import DAD_Utils
import logging
import time
import sqlite3

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
    else: DAD_Utils.logDebug("empty database")
    return rows


def closeDatabase(conn):
    conn.commit()
    conn.close()

def printDatabase(cursor):
    time1 = time.time()
    data = getStoredItems(cursor)
    for items in data:
        newString = items[2].strip('|')
        newList = newString.split('|')
        newNewList = [ele.split(",") for ele in newList]
        myItem = DAD_Utils.item(items[0],newNewList,items[1],(0,0),items[3])
        myItem.printItem()

    DAD_Utils.logDebug(f"Retrieved listed items in {time.time() - time1} seconds")


# Define the database connection
def connectDatabase():
    # Connect to the database 
    DAD_Utils.logDebug("Connecting to database...")
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