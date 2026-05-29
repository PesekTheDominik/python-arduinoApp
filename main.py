from databaze.db import *
#import tkinter as tk
import customtkinter as ctk
from ui.ui import panel

if __name__ == "__main__":
    createTables()
    root = ctk.CTk()
    app = panel(master=root)
    app.mainloop()
