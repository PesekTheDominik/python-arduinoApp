import customtkinter as ctk
from ui.ui import panel
from databaze.db import createTables 

if __name__ == "__main__":
    createTables()
    root = ctk.CTk()
    app = panel(master=root)
    root.mainloop()  
