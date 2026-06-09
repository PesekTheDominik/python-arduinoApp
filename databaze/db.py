import sqlite3
import os
import sys

def connect():
    conn = sqlite3.connect("tabulky.db")
    conn.row_factory = sqlite3.Row
    return conn

def createTables():
    conn = connect()
    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profil(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, 
            port TEXT,
            baudrate INTEGER NOT NULL,
            timeout REAL NOT NULL,
            testCmd TEXT,
            testRes TEXT DEFAULT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instrument(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            code TEXT,
            parameter INTEGER,
            info TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS method(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            info TEXT,
            dateIn DATETIME DEFAULT CURRENT_TIMESTAMP,
            deleted INTEGER 
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cmdLines(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT,
            info TEXT,
            time INTEGER,
            instrument TEXT,
            command TEXT,
            parameter INTEGER,
            code TEXT,
            timeout INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATETIME DEFAULT CURRENT_TIMESTAMP,
            method TEXT,
            executed INTEGER,
            info TEXT,
            time INTEGER,
            instrument TEXT,
            command TEXT,
            parameter INTEGER,
            code TEXT,
            response TEXT
        )
    """)
    conn.commit()
    conn.close()


def addProfil(name, port, baudrate, timeout, testCmd):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO profil (name, port, baudrate, timeout,testCmd)
        VALUES (?,?,?,?, ?) 
    """, (name, port, baudrate, timeout, testCmd))
    conn.commit()
    conn.close()

def updateProfil(name, port, baudrate, timeout, testCmd, id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE profil
        SET name = ?, port = ?, baudrate = ?, timeout = ?, testCmd = ?, testRes = ?
        WHERE id = ?
    """, (name, port, baudrate, timeout, testCmd, None, id))
    conn.commit()
    conn.close()

def getProfilId(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id 
        FROM profil
        WHERE name = ?
    """, (name, ))
    id = cursor.fetchone()
    conn.close()
    return id[0] if id else None

def getProfilName():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM profil")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def getProfilByName(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profil WHERE name = ?", (name,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

def countProfilByName(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM profil WHERE name = ?", (name,))
    count = cursor.fetchone()[0]
    conn.close()
    return count
    
def clearProfil():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profil")
    conn.commit()
    conn.close()

def deleteProfil(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DElETE FROM profil WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def addInstument(name, address):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO instrument (name,address)
        VALUES (?,?)
    """, (name, address))
    conn.commit()
    conn.close()

def addCommands(name,code ,parameter ,info ):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO commands (name, code, parameter, info)
        VALUES (?,?,?,?)
    """, (name, code, parameter, info))
    conn.commit()
    conn.close()

def getCommands():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM commands
                    ORDER BY id ASC
                   """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def getCommandsName():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM commands")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def getCommandsId(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM commands WHERE name = ?", (name,))
    id = cursor.fetchone()
    conn.close()
    return id[0] if id else None

def commandsCountByName(name):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM commands WHERE name = ?",(name,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def deleteCommand(id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM commands WHERE id = ?", (id,))
    conn.commit()
    conn.close()

def updateCommands(name, code, parameter, info, commandId):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE commands
        SET name = ?, code = ?, parameter = ?, info = ?
        WHERE id = ?   
        """, (name, code, parameter, info, commandId))
    conn.commit()
    conn.close()

def clearCommands():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM commands")
    conn.commit()
    conn.close()

def addMethod(name, info, dateIn, deleted):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO method (name, info, dateIn, deleted)
        VALUES (?,?,?,?)
    """, (name, info, dateIn, deleted))
    conn.commit()
    conn.close()

def addCmd(method, info, time, instrument, command, parameter, code, timeout):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cmdLines (method, info, time, instrument, command, parameter, code, timeout)
        VALUES (?,?,?,?,?,?,?,?)
    """, (method, info, time, instrument, command, parameter, code, timeout))

    conn.commit()
    conn.close()

def addLog(method ,executed ,info ,time,instrument,command ,parameter ,code ,response):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO log (method ,executed ,info ,time,instrument,command ,parameter ,code ,response)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (method ,executed ,info, time, instrument,command ,parameter ,code ,response))

    conn.commit()
    conn.close()