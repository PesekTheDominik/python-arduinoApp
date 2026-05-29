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
    try:
        mode = config.getboolean('program', 'theme')  
    except (configparser.NoSectionError, configparser.NoOptionError):
        mode = False  
        
    if not mode:
        ctk.set_appearance_mode("light") 
        currentMode = False
    else:
        ctk.set_appearance_mode("dark")
        currentMode = True

def changeMode(btn):
    global currentMode
    currentMode = not currentMode
    if currentMode:
        btn.configure(image=darkImg)
        ctk.set_appearance_mode("light")
    else:
        btn.configure(image=lightImg)
        ctk.set_appearance_mode("dark")

setMode()

class panel(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        
        self.pack(fill="both", expand=True)
        
        self.master.title("Control Panel")
        self.master.geometry("1400x1000") 
        self.master.resizable(False, False) 
        self.buildUi()

    def buildUi(self):
        global currentMode

        toolbar = 
        
        ctk.CTkLabel(self, text="Control Panel", font=("Helvetica", 46, "bold")).place(x=545, y=20)
        btnMode = ctk.CTkButton(self, image=darkImg, text="", command=lambda: changeMode(btnMode), bg_color="transparent", fg_color="transparent", hover_color="grey",width=32,height=32, corner_radius=28)
        btnMode.place(x=1320, y=30)  
