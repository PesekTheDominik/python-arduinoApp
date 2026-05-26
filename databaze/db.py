import sqlite3
import os
import sys

def connect():
    conn = sqlite3.connect()
    