import tkinter as tk
from tkinter import ttk, messagebox

class panel(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.master.title("ahoj")
        self.master.geometry("400x300")
        self.buildUi()

    def buildUi(self):
        self.lable = tk.Label(self, text="hello")
        self.lable.pack()
