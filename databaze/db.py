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

    cursor.execute("PRAGMA forein_keys = ON")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profil(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, 
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
            name TEXT,
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
        INSERT INTO profil (name, port, baudrate, timeout, testCmd)
        VALUES (?,?,?,?,?) 
    """, name, port, baudrate, timeout, testCmd)
    conn.commit()
    conn.close()

def addInstument(name, address):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO instrument (name,address)
        VALUES (?,?)
    """, name, address)
    conn.commit()
    conn.close()

def addCommands(name,code ,parameter ,info ):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO commands (name, code, parameter, info)
        VALUES (?,?,?,?)
    """, name, code, parameter, info)
    conn.commit()
    conn.close()

def addMethod(name, info, dateIn, deleted):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO method (name, info, dateIn, deleted)
        VALUES (?,?,?,?)
    """, name, info, dateIn, deleted)
    conn.commit()
    conn.close()

def addCmd(method, info, time, instrument, command, parameter, code, timeout):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cmdLines (method, info, time, instrument, command, parameter, code, timeout)
        VALUES (?,?,?,?,?,?,?,?)
    """, method, info, time, instrument, command, parameter, code, timeout)

    conn.commit()
    conn.close()

def addLog(method ,executed ,info ,time,instrument,command ,parameter ,code ,response):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO log (method ,executed ,info ,time,instrument,command ,parameter ,code ,response)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, method ,executed ,info, time, instrument,command ,parameter ,code ,response)

    conn.commit()
    conn.close()