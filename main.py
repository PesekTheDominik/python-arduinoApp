import customtkinter as ctk
from ui.ui import panel
from databaze.db import *
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    createTables()
    root = ctk.CTk()
    app = panel(master=root)
    root.mainloop()  
