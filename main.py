from databaze.db import *
import tkinter as tk
from ui.ui import panel

if __name__ == "__main__":
    createTables()
    root = tk.Tk()
    app = panel(master=root)
    app.mainloop()
