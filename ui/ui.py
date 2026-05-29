#import tkinter as tk
#from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image
import configparser

config = configparser.ConfigParser()
config.read("settings/settings.ini")


lightImg = ctk.CTkImage(Image.open("images/sun.png"))
darkImg = ctk.CTkImage(Image.open("images/moon.png")) 

currentMode = False

def setMode():
    global currentMode
    mode = config.getboolean('program','theme')  
    if not mode:
        ctk.set_appearance_mode("light") 
        currentMode = False
    else:
        ctk.set_appearance_mode("dark")
        currentMode = True

def changeMode(btn):
    global currentMode
    if currentMode:
        btn.configure(image=darkImg)
        btn.pack()
    else:
        btn.configure(image=lightImg)
        btn.pack()

setMode()

class panel(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        self.pack()
        self.master.title("Control Panel")
        self.master.geometry("1200x800") 
        self.master.resizable(False, False) 
        self.buildUi()

    def buildUi(self):
        global currentMode
        #self.lable = tk.Label(self, text="hello")
        #self.lable.pack()
        ctk.CTkLabel(self, text="Control Panel", font=("Helvetica", 46, "bold")).pack(pady=10, padx=10)
        btnMode = ctk.CTkButton(self, image=lightImg,text= "", command=lambda :changeMode(btnMode))
        btnMode.pack()
        changeMode(btnMode)
