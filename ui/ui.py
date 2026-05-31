import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
import configparser

config = configparser.ConfigParser()
config.read("settings/settings.ini")

lightImg = ctk.CTkImage(Image.open("images/sun2.png"))
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

def changeMode(btn, file_menu):
    global currentMode
    currentMode = not currentMode
    if currentMode:
        btn.configure(image=darkImg)
        ctk.set_appearance_mode("light")
    else:
        btn.configure(image=lightImg)
        ctk.set_appearance_mode("dark")

    config.set("program", "mode", str(currentMode))
    with open("settings/settings.ini", "w") as f:
        config.write(f)
    
    if file_menu:
        file_menu.refresh_colors()

setMode()

class StableDropdown(tk.Menu):
    def __init__(self, master):
        super().__init__(master, tearoff=0)
        self.refresh_colors()

    def refresh_colors(self):
        """Forces the native menu engine to use explicit dark/light color values."""
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        bg = "#252526" if is_dark else "#f0f0f0"
        fg = "#ffffff" if is_dark else "#000000"
        active_bg = "#37373d" if is_dark else "#e5e5e5"
        active_fg = "#ffffff" if is_dark else "#000000"
        
        self.configure(
            bg=bg, 
            fg=fg, 
            activebackground=active_bg, 
            activeforeground=active_fg,
            bd=1,
            relief="flat"
        )

    def add_action(self, label, shortcut="", command=None):
        display_text = f"{label:<20}{shortcut:>15}" if shortcut else label
        self.add_command(label=display_text, command=command)

    def show(self, widget):
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        self.post(x, y)


class panel(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        
        self.pack(fill="both", expand=True)
        
        self.master.title("Control Panel")
        self.master.geometry("1400x1000") 
        self.master.resizable(False, False) 

        self.buildUi()

    def btnCon(self, pref, sw):
        config.set("program", "timeout", str(sw.get()))
        with open("settings/settings.ini", "w") as f:
            config.write(f)
        pref.destroy()
        messagebox.showinfo("succes", "data was saved succesfully")
    

    def setup_tabs(self):
        home_label = ctk.CTkLabel(self.tabview.tab("Home"), text="Welcome Home")
        home_label.pack(pady=20)

        settings_label = ctk.CTkLabel(self.tabview.tab("Settings"), text="Settings Page")
        settings_label.pack(pady=20)

        profile_label = ctk.CTkLabel(self.tabview.tab("Profile"), text="User Profile")
        profile_label.pack(pady=20)

        about_label = ctk.CTkLabel(self.tabview.tab("About"), text="About This App")
        about_label.pack(pady=20)

    
    def preferences(self):
        pref = ctk.CTkToplevel(self)
        pref.geometry("500x400+400+400")
        pref.overrideredirect(True)
        pref.configure(fg_color=("#f0f0f0","#1c1c1c"), corner_radius=50)

        outer = ctk.CTkFrame(pref, fg_color=("#1c1c1c", "#f0f0f0"), corner_radius=3)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        inner = ctk.CTkFrame(outer, fg_color=("#f0f0f0","#1c1c1c"), corner_radius=4)
        inner.pack(fill="both", expand=True, padx=2, pady=2)

        ctk.CTkLabel(pref, text="Preferences", font=("Helvetica", 46, "bold")).place(x=30, y=20)
        ttk.Separator(pref, orient="horizontal").place(width=458, x=20, y=80)
        ctk.CTkLabel(pref, text="timeout if arduino won't answer", font=("Segoe UI", 16, "bold")).place(x=30, y=90)

        timeout = config.getboolean("program", "timeout")
        switch = ctk.CTkSwitch(inner, text="")
        if timeout:
            switch.select()
        else:
            switch.deselect()

        switch.place(x=420, y=90)

        ctk.CTkButton(inner, text="Confirm", command=lambda: self.btnCon(pref, switch), width=200).place(x=260, y=330)
        ctk.CTkButton(inner, text="Cancel", command=lambda: pref.destroy(), width=200).place(x=30, y=330)
        




    def buildUi(self):
        global currentMode

        toolbar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=("#e0e0e0", "#1e1e1e"))
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)

        self.file_menu = StableDropdown(self)
        
        self.file_menu.add_action("New Sketch", "Ctrl+N", lambda: print("New Sketch Created"))
        self.file_menu.add_action("Open...", "Ctrl+O", lambda: print("Opening file..."))
        self.file_menu.add_action("Save", "Ctrl+S", lambda: print("Saved successfully"))
        self.file_menu.add_separator()
        self.file_menu.add_action("Preferences", "Ctrl+,", command=lambda: self.preferences())
        self.file_menu.add_separator()
        self.file_menu.add_action("Quit", "Ctrl+Q", self.quit)
        
        btnFile = ctk.CTkButton(
            toolbar, 
            text="File", 
            width=60, 
            height=30, 
            corner_radius=4,
            fg_color="transparent", 
            text_color=("#000000", "#ffffff"),
            hover_color=("#cdcdcd", "#333333"),
            command=lambda: self.file_menu.show(btnFile)
        )
        btnFile.pack(side="left", padx=5, pady=5)

        #body = ctk.CTkFrame(self, fg_color="transparent")
        #body.pack(fill="both", expand=True, padx=20, pady=5)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(10, 5))

        titleLabel = ctk.CTkLabel(
            header,
            text="Control Panel",
            font=("Helvetica", 46, "bold")
        )
        titleLabel.pack(side="left", padx=20)

        btnMode = ctk.CTkButton(
            header,
            image=darkImg if not currentMode else lightImg,
            text="",
            command=lambda: changeMode(btnMode, self.file_menu),
            fg_color="transparent",
            hover_color="grey",
            width=32,
            height=32
        )
        btnMode.pack(side="right", padx=20)

        self.tabview = ctk.CTkTabview(content, width=750, height=250)
        self.tabview.pack(padx= 0, pady=20, fill="both", expand=True)

        self.tabview.add("Home")
        self.tabview.add("Settings")
        self.tabview.add("Profile")
        self.tabview.add("About")

        self.setup_tabs()