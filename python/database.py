import sqlite3
import DAD_Utils
import logging
import config
import time
import sqlite3

class error(Exception):
    pass

# Insert item into the database
def insertItem(cursor,values):
    sql = """
        INSERT INTO items (name, rarity, rolls, price, goodRoll)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(sql,values)



# retrieve config variable value
def getConfig(cursor,var):
    sql = f"SELECT {var} FROM Config"
    cursor.execute(sql)
    data = cursor.fetchone()
    return data[0] if data else None



# print entire config
def printConfig(cursor):
    cursor.execute("SELECT * FROM Config")
    rows = cursor.fetchall()
    if rows:
        return rows
    else: 
        DAD_Utils.logDebug("empty Config")
        return None



# update config variable
def setConfig(cursor,var,val):
    sql = f'UPDATE Config SET {var} = ?'
    try:
        cursor.execute(sql,(val,))
    except:
        pass



# update config in database
def updateConfig(cursor, lenCurCon):
    # build sql message to create/update Config table
    sqlDarkmode = 1 if config.darkMode else 0
    if lenCurCon == 0 or lenCurCon != config.numDatabase:
        wipeConfig(cursor)
        sql = """
            INSERT INTO Config (
            sellMin,
            sellMax,
            sellWidth,
            sellHeight,
            sellMethod,
            sellUndercut,
            sellHotkey,
            closeHotkey,
            sleepTime,
            darkMode,
            pixelValue,
            organizeMethod,
            organizeStashes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    else:
        sql = """
            UPDATE Config 
            SET sellMin = ?,
            sellMax = ?,
            sellWidth = ?,
            sellHeight = ?,
            sellMethod = ?,
            sellUndercut = ?,
            sellHotkey = ?,
            closeHotkey = ?,
            sleepTime = ?,
            darkMode = ?,
            pixelValue = ?,
            organizeMethod = ?,
            organizeStashes = ?
        """ 
    
    # get config values
    sqlInsert = [config.sellMin, config.sellMax, config.sellWidth, config.sellHeight, config.sellMethod,
              config.sellUndercut, config.sellHotkey, config.closeHotkey, config.sleepTime, sqlDarkmode, config.stashPixelVal,
              config.organizeMethod, config.organizeStashes]

    #update Config
    cursor.execute(sql,sqlInsert)
    


# delete current config
def wipeConfig(cursor):
    sql = "DROP TABLE IF EXISTS Config"
    cursor.execute(sql)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Config (
        sellMin INTEGER,
        sellMax INTEGER,
        sellWidth INTEGER,
        sellHeight INTEGER,
        sellMethod INTEGER,
        sellUndercut REAL,
        sellHotkey TEXT,
        closeHotkey TEXT,
        sleepTime REAL,
        darkMode INTEGER,
        pixelValue INTEGER,
        organizeMethod INTEGER,
        organizeStashes INTEGER           
    );
    """)




# get all stored items
def getStoredItems(cursor):
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    if rows:
        return rows
    else: 
        DAD_Utils.logDebug("empty database")
        return None
    

def wipeDatabase(cursor):
    try:
        cursor.execute("DELETE FROM Config;")
        cursor.execute("DELETE FROM items;")
    except:
        logging.debug("Error wiping db")



# close database connection
def closeDatabase(conn):
    conn.commit()
    conn.close()



# print all items in database
def printDatabase(cursor):
    time1 = time.time()
    totalGold = 0

    data = getStoredItems(cursor)
    if data:
        for item in data:
            try:
                DAD_Utils.logDebug(f"{item} found items in database")
                newString = item[2].strip('|')
                newList = newString.split('|')
                newNewList = [ele.split(",") for ele in newList]
                myItem = DAD_Utils.item(item[0],newNewList,item[1],(-1,-1),None,item[3])
                myItem.printItem(True)
                totalGold += int(item[3])
            except Exception as e:
                DAD_Utils.logDebug(f"{e} Corrupted/invalid item read in database")

    DAD_Utils.logDebug(f"Retrieved listed items in {time.time() - time1} seconds")
    
    return totalGold



# Define the database connection
def connectDatabase():
    # Connect to the database 
    DAD_Utils.logDebug("Connecting to database...")
    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()

    # Create items table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Items (
        name TEXT,
        rarity TEXT,
        rolls TEXT,
        price INTEGER,
        goodRoll INTEGER
    );
    """)

    # Create config table if it doesnt exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Config (
        sellMin INTEGER,
        sellMax INTEGER,
        sellWidth INTEGER,
        sellHeight INTEGER,
        sellMethod INTEGER,
        sellUndercut REAL,
        sellHotkey TEXT,
        closeHotkey TEXT,
        sleepTime REAL,
        darkMode INTEGER,
        pixelValue INTEGER,
        organizeMethod INTEGER,
        organizeStashes INTEGER           
    );
    """)

    return conn, cursor

