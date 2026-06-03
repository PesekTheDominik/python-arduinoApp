import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
import configparser
from serial.tools import list_ports
from databaze.db import *

config = configparser.ConfigParser()
config.read("settings/settings.ini")

lightImg = ctk.CTkImage(Image.open("images/sun2.png"))
darkImg = ctk.CTkImage(Image.open("images/moon.png")) 
texts = ["Set up Device","Edit methods", "Edit commands","Run", "Log"]

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
    global texts
    def __init__(self, master=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        
        self.pack(fill="both", expand=True)
        
        self.master.title("Control Panel")
        self.master.geometry("1400x1000+230+30") 
        self.master.resizable(False, False) 

        self.buildUi()

    def btnCon(self, pref, sw):
        config.set("program", "timeout", str(sw.get()))
        with open("settings/settings.ini", "w") as f:
            config.write(f)
        pref.destroy()
        messagebox.showinfo("succes", "data was saved succesfully")
    
    def serialPorts(self):
        ports = list_ports.comports()
        return [p.device for p in ports]


    def setup_tabs(self):
        baudRates = ["300","1200","2400","4800","9600","19200","38400","57600","115200","230400","460800","921600",]
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Select your device profile: ",font=("Segoe UI", 16, "bold")).place(x=30,y=20)
        profilNames = getProfilName()
        cbProfil = ctk.CTkComboBox(self.tabview.tab(texts[0]), values=profilNames, state="readonly",font=("Segoe UI", 16, "bold")).place(x=250, y=20)
        ctk.CTkFrame( self.tabview.tab(texts[0]), width=2, height=40, fg_color="#666666").place(x=420, y=15)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Name: ",font=("Segoe UI", 16, "bold")).place(x=440, y=20)
        tbName = ctk.CTkTextbox(self.tabview.tab(texts[0]), width=180, height=20,border_width=2, border_color="#1492c4").place(x=500, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Port: ", font=("Segoe UI", 16, "bold")).place(x=730, y=20)
        ports = self.serialPorts()
        cbPorts = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=180, height=30, values=ports,state="readonly").place(x=780,y=20)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="BaudRate: ", font=("Segoe UI", 16, "bold")).place(x=1010, y=20)
        cbBaudRate = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=180, height=30, values=baudRates, state="readonly").place(x=1100, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Test command: ", font=("Segoe UI", 16, "bold")).place(x=30, y=60)
        commands = getCommandsName()
        cbBaudRate = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=180, height=30, values=commands, state="readonly").place(x=250, y=60)

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


    def newCommand(self, comName, code, par, info, Tcomand, wadd):
        proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede", parent=wadd)
        if proceed:
            Fname = comName.get("1.0", "end").strip()
            Fcode = code.get("1.0", "end").strip()
            Finfo = info.get("1.0", "end").strip()    
            if Fname and Fcode and Finfo :
                addCommands(Fname,Fcode, par.get(), Finfo)
                self.reloadCom(Tcomand)
            else:
                tk.messagebox.showwarning(title="warning", message="You must fill all of the information when creating a command", parent=wadd)
        else:
            return
        
    def editCommand(self, comName, code, par, info, Tcomand, wadd):
        proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede", parent=wadd)
        if proceed:
            Fname = comName.get("1.0", "end").strip()
            Fcode = code.get("1.0", "end").strip()
            Finfo = info.get("1.0", "end").strip()    
            if Fname and Fcode and Finfo :
                id = getCommandsId(Fcode)
                updateCommands(Fname, Fcode,par.get() ,Finfo,id)
                self.reloadCom(Tcomand)
            else:
                tk.messagebox.showwarning(title="warning", message="You must fill all of the information when creating a command", parent=wadd)
        else:
            return
    

    def reloadCom(self, Tcomand):
        Tcomand.delete(*Tcomand.get_children())

        rows = getCommands()

        for row in rows:
            name = row[1]
            code = row[2]
            parameter = row[3]
            info = row[4]
            Tcomand.insert("","end", values=(name, code, parameter, info))




    def addCom(self):
        wadd = ctk.CTkToplevel(self)
        wadd.geometry("900x610+400+200")
        wadd.overrideredirect(True)
        wadd.configure(fg_color=("#f0f0f0","#1c1c1c"), corner_radius=50)   
        outer = ctk.CTkFrame(wadd, fg_color=("#1c1c1c", "#f0f0f0"), corner_radius=3)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        inner = ctk.CTkFrame(outer, fg_color=("#f0f0f0","#1c1c1c"), corner_radius=4)
        inner.pack(fill="both", expand=True, padx=2, pady=2)          
        ctk.CTkLabel(wadd, text="add commands", font=("Helvetica", 46, "bold")).place(x=30, y=20)

        Tcomand = ttk.Treeview(
            wadd,
            columns=("name", "code", "parameter", "info"),
            show="headings"
        )

        Tcomand.heading("name", text="name")
        Tcomand.heading("code", text="code")
        Tcomand.heading("parameter", text="parameter")
        Tcomand.heading("info", text="info")

        rows = getCommands()

        for row in rows:
            name = row[1]
            code = row[2]
            parameter = row[3]
            info = row[4]
            Tcomand.insert("","end", values=(name, code, parameter, info))

        def Tchange(event):
            btnNew.configure(text="Edit", command=lambda: self.editCommand(tbComName, tbCode, swPar, tbinfo, Tcomand, wadd))
            btnDelete.configure(text="Delete Selected")             

        Tcomand.bind("<<TreeviewSelect>>", Tchange)

        Tcomand.place(x=20, y=100, width=850, height=300)
        scrollbar = ttk.Scrollbar(
            wadd,
            orient="vertical",
            command=Tcomand.yview
        )

        Tcomand.configure(yscrollcommand=scrollbar.set)

        scrollbar.place(x=852, y=101, height=298)
        
        ctk.CTkButton(wadd,font=("Helvetica", 20 ,"bold"), text="X", command=lambda: wadd.destroy(), width=30, height=30, text_color=("black", "white"),border_width=2, border_color=("black","white") ,fg_color="transparent", hover_color="grey", corner_radius=15).place(x=810, y=37)
        ctk.CTkLabel(wadd, text="name: ", font=("Segoe UI", 16, "bold")).place(x=70, y=420)
        tbComName = ctk.CTkTextbox(wadd, width=200, height=20,border_width=2, border_color="#1492c4")
        tbComName.place(x=140, y=420) 
        ctk.CTkLabel(wadd, text="code: ", font=("Segoe UI", 16, "bold")).place(x=380, y=420)
        tbCode = ctk.CTkTextbox(wadd, width=200, height=20,border_width=2, border_color="#1492c4")
        tbCode.place(x=440, y=420) 
        ctk.CTkLabel(wadd, text="parameter: ", font=("Segoe UI", 16, "bold")).place(x=680, y=420)
        swPar = ctk.CTkSwitch(wadd, text="")
        swPar.place(x= 780, y=423)
        ctk.CTkLabel(wadd, text="info: ", font=("Segoe UI", 16, "bold")).place(x=50, y=470)
        tbinfo = ctk.CTkTextbox(wadd, width=740, height=20,border_width=2, border_color="#1492c4")
        tbinfo.place(x=100, y=470) 
        btnDelete = ctk.CTkButton(wadd, text="Delete All", font=("Segoe UI", 16, "bold"), command=lambda: print("n"), width=370, text_color_disabled="white", fg_color="red",hover_color="#610000", text_color="white")
        btnDelete.place(x=65, y=520)
        btnNew = ctk.CTkButton(wadd, text="New", font=("Segoe UI", 16, "bold"), command=lambda: self.newCommand(tbComName, tbCode, swPar, tbinfo, Tcomand, wadd), width=370, state="normal", text_color_disabled="white", fg_color="green",hover_color="#00610d", text_color="white")
        btnNew.place(x=465, y=520)
        ctk.CTkButton(wadd, text="clear selection", font=("Segoe UI", 16, "bold"), command=lambda: clearCom(), width=770).place(x=65, y=560)

        def clearCom():
            Tcomand.selection_remove(Tcomand.selection())
            btnNew.configure(text="New")
            btnDelete.configure(text="Delete All")             

    def buildUi(self):
        global currentMode

        toolbar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=("#e0e0e0", "#1e1e1e"))
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)

        self.file_menu = StableDropdown(self)
        
        self.file_menu.add_separator()
        self.file_menu.add_action("add Commands", "ctrl+a", command=lambda: self.addCom())
        self.file_menu.add_action("Preferences", "Ctrl+n", command=lambda: self.preferences())
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
        self.tabview.pack(padx= 10, pady=20, fill="both", expand=True)
        self.tabview._segmented_button.configure(
            font=("helvetica", 20, "bold"),
            border_width=1,
            text_color=("#000000", "#ffffff"),
            text_color_disabled=("#777777", "#777777"),
            fg_color=("#e0e0e0", "#2a2a2a"),
            selected_color=("#d0d0d0", "#3a3a3a"),
            unselected_color=("#f0f0f0", "#1f1f1f"),
            selected_hover_color=("#c8c8c8", "#444444"),
            unselected_hover_color=("#dddddd", "#2a2a2a"),
        )



        self.tabview.add(texts[0])
        self.tabview.add(texts[1])
        self.tabview.add(texts[2])
        self.tabview.add(texts[3])
        self.tabview.add(texts[4])

        self.setup_tabs()