import customtkinter as ctk
from ui.ui import panel
from databaze.db import *

if __name__ == "__main__":
    createTables()
    clearProfil()
    addProfil("arduino", "COM9", 11000, 2.0, "S")
    root = ctk.CTk()
    app = panel(master=root)
    root.mainloop()  
