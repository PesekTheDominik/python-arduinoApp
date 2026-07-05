import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
import configparser
from serial.tools import list_ports
from databaze.db import *
from arduino.arduino import *
from dataclasses import dataclass

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

config = configparser.ConfigParser()
config.read(resource_path("settings/settings.ini"))

lightImg = ctk.CTkImage(Image.open(resource_path("images/sun2.png")))
darkImg = ctk.CTkImage(Image.open(resource_path("images/moon.png"))) 
texts = ["Set up Device","Create methods", "Configure Methods","Run", "Log"]
connection = arduino()

currentMode = False

SelectedProfil = None

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
    with open(resource_path("settings/settings.ini"), "w") as f:
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
    global texts, SelectedProfil
    def __init__(self, master=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        
        self.pack(fill="both", expand=True)
        
        self.master.title("Control Panel | Arduino disconnected")
        self.master.geometry("1400x1000+230+30") 
        self.master.resizable(False, False) 

        self.buildUi()

    def btnCon(self, pref, sw1, sw2):
        config.set("program", "timeout", str(sw1.get()))
        config.set("program", "ClearProfilSelection", str(sw2.get()))
        with open("settings/settings.ini", "w") as f:
            config.write(f)
        pref.destroy()
        messagebox.showinfo("succes", "data was saved succesfully")
    
    def serialPorts(self):
        ports = list_ports.comports()
        return [p.device for p in ports]


    def setup_tabs(self):
        #--------------------------tab 1------------------------------------------------#
        profilMode = {"value": False}
        baudRates = ["300","1200","2400","4800","9600","19200","38400","57600","115200","230400","460800","921600",]
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Select your device profile: ",font=("Segoe UI", 16, "bold")).place(x=30,y=20)
        profilNames = getProfilName()
        profilLen = len(profilNames)
        btnDelete = ctk.CTkButton(self.tabview.tab(texts[0]),width=160, height=30, command=lambda: delAllProfils(),font=("Segoe UI", 16, "bold"), text="Delete all")
        if (profilLen) != 0:
            btnDelete.place(x=930, y=80)

        cbProfil = ctk.CTkComboBox(self.tabview.tab(texts[0]), values=profilNames, state="readonly",font=("Segoe UI", 16, "bold"),command=lambda choice: loadProfil(choice),width=180, height=30)
        cbProfil.place(x=250, y=20)
        ctk.CTkFrame( self.tabview.tab(texts[0]), width=2, height=40, fg_color="#666666").place(x=450, y=15)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Name: ",font=("Segoe UI", 16, "bold")).place(x=470, y=20)
        tbName = ctk.CTkTextbox(self.tabview.tab(texts[0]), width=180, height=20,border_width=2, border_color="#1492c4")
        tbName.place(x=530, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Port: ", font=("Segoe UI", 16, "bold")).place(x=760, y=20)
        ports = self.serialPorts()
        cbPorts = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=180, height=30, values=ports,state="readonly")
        cbPorts.place(x=810,y=20)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="BaudRate: ", font=("Segoe UI", 16, "bold")).place(x=1040, y=20)
        cbBaudRate = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=180, height=30, values=baudRates, state="readonly")
        cbBaudRate.place(x=1130, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="timeout", font=("Segoe UI", 16, "bold")).place(x=30, y=80)
        tbTimeout = ctk.CTkTextbox(self.tabview.tab(texts[0]), width=120, height=20,border_width=2, border_color="#1492c4")
        tbTimeout.place(x=120, y=80)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Test command: ", font=("Segoe UI", 16, "bold")).place(x=280, y=80)

        cbCommands = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=150, height=30 , state="readonly", command=lambda choice: loadCommands(choice))
        tbParameter = ctk.CTkTextbox(self.tabview.tab(texts[0]), width=100, height=30,border_width=2, border_color="#1492c4")

        cbCommands.place(x=430, y=80)

        btnEditor = ctk.CTkButton(self.tabview.tab(texts[0]),width=160,  height=30, command=lambda: newProfil(),font=("Segoe UI", 16, "bold"), text="New")
        btnClear = ctk.CTkButton(self.tabview.tab(texts[0]), height=30,width=160, command=lambda: clearProf(),font=("Segoe UI", 16, "bold"), text="Clear Selection")
        btnCancel = ctk.CTkButton(self.tabview.tab(texts[0]), height=30,width=160, command=lambda: cancelProf(),font=("Segoe UI", 16, "bold"), text="Cancel")
        conn = True
        btnConnect = ctk.CTkButton(self.tabview.tab(texts[0]), width=650, height=40, text="Connect",font=("Segoe UI", 16, "bold"), command=lambda: arduinoConnect(conn))

        addiLbl = ctk.CTkLabel(self.tabview.tab(texts[0]), text="try addition command:",font=("Segoe UI", 16, "bold"))
        cbAddi = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=150, height=30, state="readonly", command=lambda choice: loadAddi(choice))
        tbAddi = ctk.CTkTextbox(self.tabview.tab(texts[0]), width=100, height=30,border_width=2, border_color="#1492c4" )
        btnAddi = ctk.CTkButton(self.tabview.tab(texts[0]), height=30,width=160, command=lambda: sendAddi(),font=("Segoe UI", 16, "bold"), text="Test")
        lblAns = ctk.CTkLabel(self.tabview.tab(texts[0]), text="Answer: ",font=("Segoe UI", 16, "bold"))    
        tbAns = ctk.CTkTextbox(self.tabview.tab(texts[0]), state="disabled", width=410, height=30,border_width=2, border_color="#1492c4")

        tbName.configure(state="disabled", border_color="#cc1a0d")
        cbPorts.configure(state="disabled", border_color="#cc1a0d")
        cbBaudRate.configure(state="disabled", border_color="#cc1a0d")
        tbTimeout.configure(state="disabled", border_color="#cc1a0d")
        cbCommands.configure(state="disabled", border_color="#cc1a0d")

        btnEditor.place(x=730, y=80)

        def cancelProf():
            clearInputs()
            profilMode["value"] = False
            cbProfil.configure(values=getProfilName())
            tbName.configure(state="disabled", border_color="#cc1a0d")
            cbPorts.configure(state="disabled", border_color="#cc1a0d")

            cbBaudRate.configure(state="disabled", border_color="#cc1a0d")
            tbTimeout.configure(state="disabled", border_color="#cc1a0d")
            cbCommands.configure(state="disabled", border_color="#cc1a0d")
            cbProfil.configure(state="normal", border_color=("gray70", "gray30"))
            btnEditor.configure(text="New")


        def sendAddi():
            print()

        def loadCommands(choice):
            par = getCommandsPar(choice)
            if par == 1:
                tbParameter.place(x=600, y=80)
            else:
                tbParameter.place_forget()

        def loadAddi(choice):
            par = getCommandsPar(choice)
            if par == 1:
                tbAddi.place(x=380, y=190)
            else:
                tbAddi.place_forget()

        def arduinoConnect(conn):
            global connection

            profil = getProfilByName(cbProfil.get())
            connection.setUp(profil[2],profil[3],profil[4])
            if conn:
                y = connection.connectToArduino()
                if y == True:         
                    conn = False
                    ctk.CTkLabel(self.tabview.tab(texts[0]), text="Test Cmd result: ", font=("Segoe UI", 16, "bold")).place(x=750, y=145)
                    tbRes = ctk.CTkTextbox(self.tabview.tab(texts[0]), state="disabled", width=410, height=30,border_width=2, border_color="#1492c4")
                    tbRes.place(x=900, y=145)
                    self.master.title("Control Panel | Arduino connected")
                    reply = connection.send(getCommandCode(profil[5]) + tbParameter.get("1.0", "end"))
                    if reply == False:
                        updateProfilTest(None, profil[0])
                    else:
                        updateProfilTest(reply, profil[0])
                    tbRes.configure(state="normal")
                    tbRes.delete("1.0", "end")
                    tbRes.insert("1.0", reply)
                    tbRes.configure(state="disabled")
                    addiLbl.place(x=20, y=190)
                    cbAddi.place(x=210, y=190)
                    btnAddi.place(x = 510, y=190)
                    lblAns.place(x=810, y=190)
                    tbAns.place(x=900, y=190)
                    btnConnect.configure(text="Disconnect")
                else:
                    tk.messagebox.showwarning("Warning", y)
            else:
                self.master.title("Control Panel | Arduino disconnected")
                connection.closeCommunication()
                conn = True
                
    
        def loadProfil(choice):
            global SelectedProfil
            profil = getProfilByName(choice)
            SelectedProfil = profil[1]
            tbName.delete("1.0", "end")
            tbName.insert("1.0", profil[1])
            cbPorts.set(profil[2])
            cbBaudRate.set(profil[3])
            tbTimeout.delete("1.0", "end")
            tbTimeout.insert("1.0", profil[4])
            cbCommands.set(profil[5])
            btnClear.place(x=1130, y=80)   
            btnEditor.configure(text="Edit", command=lambda: editProfil())        
            btnDelete.configure(text="Delete selected", command=lambda: delProfil())
            btnConnect.place(x=20, y=140)


        def delAllProfils():
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede? \nBy editing you will delete testCmd result")
            if proceed:
                clearProfil()
                clearInputs()
                cbProfil.configure(values=getProfilName())



        def editProfil():
            if profilMode["value"]:
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede? \nBy editing you will delete testCmd result")
                if proceed:
                    profilMode["value"] = False
                    btnClear.place(x=1130, y=80)
                    btnCancel.place_forget()
                    id = getProfilId(cbProfil.get())
                    Pname = tbName.get("1.0", "end").strip()
                    Pport = cbPorts.get()

                    Pbaud = int(cbBaudRate.get())
                    Pcommand = cbCommands.get()
                    Ptimeout = float(tbTimeout.get("1.0", "end").strip())
                    if Pname and Ptimeout and Pport and Pbaud and Pcommand:
                        if countProfilByName(Pname) < 2:
                            updateProfil(Pname, Pport, Pbaud, Ptimeout,Pcommand, id)
                            cbProfil.configure(values=getProfilName())
                            tbName.configure(state="disabled", border_color="#cc1a0d")
                            cbPorts.configure(state="disabled", border_color="#cc1a0d")

                            cbBaudRate.configure(state="disabled", border_color="#cc1a0d")
                            tbTimeout.configure(state="disabled", border_color="#cc1a0d")
                            cbCommands.configure(state="disabled", border_color="#cc1a0d")
                            cbProfil.configure(state="normal", border_color=("gray70", "gray30"))
                            if int(config.get("program", "clearprofilselection")) == 1:
                                clearInputs()
                                btnEditor.configure(text="New")
                            else:
                                btnEditor.configure(text="Edit")
                            loadProfilesTable()
                        else:
                            tk.messagebox.showwarning(title="Warning", message="Names have to be unique")
                    else:
                        tk.messagebox.showwarning(title="Warning", message="All inputs must be filled in to create a profile")
            else:
                profilMode["value"] = True 
                tbName.configure(state="normal", border_color="#1492c4")
                cbPorts.configure(state="normal", border_color=("gray70", "gray30"))
                cbBaudRate.configure(state="normal", border_color=("gray70", "gray30"))
                tbTimeout.configure(state="normal", border_color="#1492c4")
                cbCommands.configure(state="normal", border_color=("gray70", "gray30"))
                profil = getProfilByName(cbProfil.get())
                commands = [c[:-1] for c in getCommandsNameByProfil(profil[1])]
                cbCommands.set("")
                cbAddi.set("")
                cbCommands.configure(values=commands)
                cbAddi.configure(values=commands)
                btnClear.place_forget()
                btnCancel.place(x=1130, y=80) 

                btnEditor.configure(text="Save")
                
                if profil:
                    tbName.delete("1.0", "end")
                    tbName.insert("1.0", profil[1])
                    cbPorts.set(profil[2])
                    cbBaudRate.set(profil[3])
                    tbTimeout.delete("1.0", "end")
                    tbTimeout.insert("1.0", profil[4])
                    cbCommands.set(profil[5])

        def delProfil():
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede? \nBy editing you will delete testCmd result")
            if proceed:
                if cbProfil.get():
                    deleteProfil(cbProfil.get())
                    clearInputs()
                    cbProfil.configure(values=getProfilName())
                    loadProfilesTable()

        def newProfil():
            if profilMode["value"]:
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
                if proceed:
                    Pname = tbName.get("1.0", "end").strip()
                    Pport = cbPorts.get()
                    Pbaud = cbBaudRate.get()
                    Pcommand = cbCommands.get()
                    Ptimeout = tbTimeout.get("1.0", "end").strip()
                    profilMode["value"] = False 
                    if Pname and Ptimeout and Pport and Pbaud and Pcommand:
                        if countProfilByName(Pname) < 1:
                            addProfil(Pname, Pport, Pbaud, Ptimeout, Pcommand)
                            profilNames = getProfilName()
                            cbProfil.configure(values=profilNames)
                            tbName.configure(state="disabled", border_color="#cc1a0d")
                            cbPorts.configure(state="disabled", border_color="#cc1a0d")
                            cbBaudRate.configure(state="disabled", border_color="#cc1a0d")
                            tbTimeout.configure(state="disabled", border_color="#cc1a0d")
                            cbCommands.configure(state="disabled", border_color="#cc1a0d")
                            cbProfil.configure(state="normal", border_color=("gray70", "gray30"))
                            btnEditor.configure(text="New")
                            btnCancel.place_forget()
                            btnClear.place(x=1130, y=80) 
                            loadProfilesTable()
                            clearInputs()
                            if profilLen == 0:
                                profilLen
                            if profilLen == 0:
                                btnDelete.place(x=930, y=80)
                        else:    
                            tk.messagebox.showwarning(title="Warning", message="Names have to be unique")
                    else:
                        tk.messagebox.showwarning(title="Warning", message="All inputs must be filled in to create a profile")
            else:
                profilMode["value"] = True
                btnEditor.configure(text="Save")
                tbName.configure(state="normal", border_color="#1492c4")
                cbPorts.configure(state="normal", border_color=("gray70", "gray30"))
                cbBaudRate.configure(state="normal", border_color=("gray70", "gray30"))
                tbTimeout.configure(state="normal", border_color="#1492c4")
                cbCommands.configure(state="normal", border_color=("gray70", "gray30"))
                cbProfil.configure(state="disabled", border_color="#cc1a0d")
                cbCommands.set("")
                cbAddi.set("")
                btnClear.place_forget()
                btnCancel.place(x=1130, y=80) 

        def clearProf():
            tProfil.selection_remove(tProfil.selection())
            clearInputs()
            btnEditor.configure(text="New", command=lambda: newProfil())       
            btnDelete.configure(text="Delete all", command=lambda: delAllProfils())
            btnConnect.place_forget()
            btnClear.place_forget()
            SelectedProfil = None

        def clearInputs():
            cbCommands.set("")
            cbBaudRate.set("")
            cbPorts.set("")
            cbProfil.set("")
            tbTimeout.delete("1.0", "end")
            tbName.delete("1.0", "end")

            btnClear.place_forget()

        def loadProfilesTable():
            tProfil.delete(*tProfil.get_children())

            rows = getProfil()

            for row in rows:
                id = row[0]
                name = row[1]
                port = row[2]
                baud = row[3]
                timeout = row[4]
                testC = row[5]
                testR = row[6]
                tProfil.insert("","end", values=(id, name, port, baud, timeout, testC, testR))

        def tProfilChange(event):
            selected = tProfil.selection()

            if selected:
                values = tProfil.item(selected[0], "values")
                cbProfil.set(values[1])
                loadProfil(values[1])

        fProfil = ctk.CTkFrame(
            self.tabview.tab(texts[0]),
            width=1500,
            height=1000
        )

        fProfil.place(x=30, y=240)

        columns = ("id", "name", "port", "baudrate", "timeout", "testCmd", "testRes")

        tProfil = ttk.Treeview(fProfil, columns=columns, show="headings", height=23)

        tProfil.heading("id", text="ID")
        tProfil.heading("name", text="Name")
        tProfil.heading("port", text="Port")
        tProfil.heading("baudrate", text="Baudrate")
        tProfil.heading("timeout", text="Timeout")
        tProfil.heading("testCmd", text="Test Command")
        tProfil.heading("testRes", text="Test Result")

        tProfil.column("id", width=100, anchor="center")
        tProfil.column("name", width=200)
        tProfil.column("port", width=100)
        tProfil.column("baudrate", width=200)
        tProfil.column("timeout", width=200)
        tProfil.column("testCmd", width=200)
        tProfil.column("testRes", width=250)

        tProfil.pack(side="left", fill="both", expand=True)

        scrollY = ttk.Scrollbar(fProfil, orient="vertical", command=tProfil.yview)

        tProfil.configure(yscrollcommand=scrollY.set)

        scrollY.place(x=1234, y=0, height=1000)
        loadProfilesTable()

        tProfil.bind("<<TreeviewSelect>>", tProfilChange)

        #--------------------------tab 2------------------------------------------------#
        methodMode = {"value": False}
        fMethod = ctk.CTkFrame(
            self.tabview.tab(texts[1]),
            width=2000,
            height=1000
        )

        fMethod.place(x=70, y=240)

        columns = ("id", "name", "info", "dateIn", "deleted")

        tMethod = ttk.Treeview(
            fMethod,
            columns=columns,
            show="headings",
            height=23
        )

        tMethod.heading("id", text="ID")
        tMethod.heading("name", text="Name")
        tMethod.heading("info", text="Info")
        tMethod.heading("dateIn", text="Created")
        tMethod.heading("deleted", text="Deleted")

        tMethod.column("id", width=80, anchor="center")
        tMethod.column("name", width=250)
        tMethod.column("info", width=500)
        tMethod.column("dateIn", width=250)
        tMethod.column("deleted", width=100, anchor="center")

        tMethod.pack(side="left", fill="both", expand=True)

        scrollY = ttk.Scrollbar(fMethod, orient="vertical", command=tMethod.yview)

        tMethod.configure(yscrollcommand=scrollY.set)

        scrollY.place(x=1234, y=0, height=1000)


        methodNames = getMethodNames()
        ctk.CTkLabel(self.tabview.tab(texts[1]), text="Select Method:", font=("Segoe UI", 16, "bold")).place(x=30, y=20)
        cbMethod = ctk.CTkComboBox(self.tabview.tab(texts[1]), values=methodNames, state="readonly",font=("Segoe UI", 16, "bold"),command=lambda choice: loadMethod(choice),width=180, height=30)
        cbMethod.place(x = 180, y=20)
        ctk.CTkFrame( self.tabview.tab(texts[1]), width=2, height=40, fg_color="#666666").place(x=380, y=15)
        ctk.CTkLabel(self.tabview.tab(texts[1]), text="Method name:", font=("Segoe UI", 16, "bold")).place(x=400, y=20)
        tbMetName = ctk.CTkTextbox(self.tabview.tab(texts[1]), width=150, height=30,border_width=2, border_color="#1492c4")
        tbMetName.place(x=540, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[1]), text="info :", font=("Segoe UI", 16, "bold")).place(x=720, y=20) 
        tbMetInfo = ctk.CTkTextbox(self.tabview.tab(texts[1]), width=320, height=30,border_width=2, border_color="#1492c4")
        tbMetInfo.place(x=790, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[1]), text="Deleted :", font=("Segoe UI", 16, "bold")).place(x=1150, y=20) 
        swDeleted = ctk.CTkSwitch(self.tabview.tab(texts[1]), text="")
        swDeleted.place(x=1250,y=20)
        btnMetEditor = ctk.CTkButton(self.tabview.tab(texts[1]),width=590,  height=30, command=lambda: newMethod(),font=("Segoe UI", 16, "bold"), text="New")
        btnMetEditor.place(x=60,y=80)
        btnMetDelete = ctk.CTkButton(self.tabview.tab(texts[1]),width=590,  height=30, command=lambda: metDeleteAll(),font=("Segoe UI", 16, "bold"), text="Delete All")
        btnMetDelete.place(x=680, y=80)
        btnMetClear =  ctk.CTkButton(self.tabview.tab(texts[1]),width=1212,  height=30, command=lambda: clearMetSelect(),font=("Segoe UI", 16, "bold"), text="Clear Select")
        btnMetClear.place(x=59, y=130)
        btnMetCancel = ctk.CTkButton(self.tabview.tab(texts[1]),width=1212,  height=30, command=lambda: cancelMet(),font=("Segoe UI", 16, "bold"), text="Cancel")


        tbMetName.configure(state="disabled", border_color="#cc1a0d")
        tbMetInfo.configure(state="disabled", border_color="#cc1a0d")
        swDeleted.configure(state="disabled")

        def cancelMet():
            methodMode["value"] = False
            cbMethod.configure(values=methodNames)
            tbMetName.configure(state="disabled", border_color="#cc1a0d")
            tbMetInfo.configure(state="disabled", border_color="#cc1a0d")
            swDeleted.configure(state="disabled")
            btnEditor.configure(text="New")
            btnMetClear.place(x=59, y=130)
            btnMetCancel.place_forget()
            clearMetInputs()


        def loadMethodTable():
            tMethod.delete(*tMethod.get_children())

            rows = getMethod()

            for row in rows:
                id = row[0]
                name = row[1]
                info = row[2]
                dateIn = row[3]
                deleted = row[4]
                tMethod.insert("","end", values=(id, name, info, dateIn, deleted))

        loadMethodTable()

        def metDeleteAll(): 
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
            if proceed:
                clearMethod()
                loadMethodTable()
                clearMetInputs()

        def metDelete(): 
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
            if proceed:
                deteleMethod(cbMethod.get())
                loadMethodTable()
                clearMetInputs()

        def clearMetSelect():
            tMethod.selection_remove(tMethod.selection())                            
            clearInputs()
            btnMetEditor.configure(text="New", command=lambda: newMethod())       
            btnMetDelete.configure(text="Delete all", command=lambda: metDeleteAll())
            btnConnect.place_forget()
            btnClear.place_forget()

        def tMethodChange(event):
            selected = tMethod.selection()

            if selected:
                values = tMethod.item(selected[0], "values")
                cbMethod.set(values[1])
                loadMethod(values[1])

        tMethod.bind("<<TreeviewSelect>>", tMethodChange)

        def loadMethod(choice):
            method = getMethodByName(choice)
            tbMetName.delete("1.0", "end")
            tbMetName.insert("1.0", method[1])
            tbMetInfo.delete("1.0", "end")
            tbMetInfo.insert("1.0", method[2])
            if method[3] == 1:
                swDeleted.select()
            else:
                swDeleted.deselect()

            btnMetEditor.configure(text="Edit", command=lambda: editMethod())
            btnMetDelete.configure(text="Delete Selected", command=lambda: metDelete())


        def clearMetInputs():
            cbMethod.set("")
            tbMetName.delete("1.0", "end")
            tbMetInfo.delete("1.0", "end")
            swDeleted.deselect()

        def editMethod():
            if methodMode["value"]:
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
                if proceed:
                    methodMode["value"] = False
                    Mname = tbMetName.get("1.0", "end").strip()
                    Minfo = tbMetInfo.get("1.0", "end").strip()
                    if Mname and Minfo:
                        if countMethodByName(Mname) < 2:
                            id = getMethodId(cbMethod.get())
                            updateMethod(Mname, Minfo, swDeleted.get(), id)
                            tbMetName.configure(state="disabled", border_color="#cc1a0d")
                            tbMetInfo.configure(state="disabled", border_color="#cc1a0d")
                            swDeleted.configure(state="disabled")
                            btnEditor.configure(text="Edit")
                            btnMetClear.place(x=59, y=130)
                            btnMetCancel.place_forget()
                            if int(config.get("program", "clearprofilselection")) == 1:
                                clearMetInputs()
                                btnEditor.configure(text="New", command=lambda: newMethod())
                            
                            loadMethodTable()
                        else:
                            tk.messagebox.showwarning(title="Warning", message="Names have to be unique")
                    else:
                        tk.messagebox.showwarning(title="Warning", message="all inputs must be filled in to create a profile")
            else:
                methodMode["value"] = True
                btnEditor.configure(text="Save")
                tbMetName.configure(state="normal", border_color="#1492c4")
                tbMetInfo.configure(state="normal", border_color="#1492c4")
                swDeleted.configure(state="normal")
                btnEditor.configure(text="Save")
                btnMetCancel.place(x=59, y=130)
                btnMetClear.place_forget()

        def newMethod():
            if methodMode["value"]:
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
                if proceed:
                    methodMode["value"] = False
                    Mname = tbMetName.get("1.0", "end").strip()
                    Minfo = tbMetInfo.get("1.0", "end").strip()
                    if Mname and Minfo:
                        if countMethodByName(Mname) < 1:
                            addMethod(Mname, Minfo, swDeleted.get())
                            methodNames = getMethodNames()
                            cbMethod.configure(values=methodNames)
                            tbMetName.configure(state="disabled", border_color="#cc1a0d")
                            tbMetInfo.configure(state="disabled", border_color="#cc1a0d")
                            swDeleted.configure(state="disabled")
                            btnEditor.configure(text="New")
                            btnMetClear.place(x=59, y=130)
                            btnMetCancel.place_forget() 
                            loadMethodTable()
                            clearMetInputs()
                        else:
                            tk.messagebox.showwarning(title="Warning", message="Names have to be unique")
                    else:
                        tk.messagebox.showwarning(title="Warning", message="all inputs must be filled in to create a profile")
            else:
                methodMode["value"] = True
                tbMetName.configure(state="normal", border_color="#1492c4")
                tbMetInfo.configure(state="normal", border_color="#1492c4")
                swDeleted.configure(state="normal")
                btnEditor.configure(text="Save")
                btnMetCancel.place(x=59, y=130)
                btnMetClear.place_forget()

        #--------------------------tab 3----------------------------------------------#
        lineMode = {"value":False}

        fcmd = ctk.CTkFrame(
            self.tabview.tab(texts[2]),
            width=1500,
            height=1000
        )

        fcmd.place(x=30, y=240)


        columns = ("id","time", "state", "description", "instrument", "command", "parameter", "code")

        tcmd = ttk.Treeview(fcmd, columns=columns, show="headings", height=23)

        tcmd.heading("id", text="id")
        tcmd.heading("time", text="time")
        tcmd.heading("state", text="state")
        tcmd.heading("description", text="description")
        tcmd.heading("instrument", text="instrument")
        tcmd.heading("command", text="command")
        tcmd.heading("parameter", text="parameter")
        tcmd.heading("code", text="code")

        tcmd.column("id", width=70)
        tcmd.column("time", width=170)
        tcmd.column("state", width=100)
        tcmd.column("description", width=250)
        tcmd.column("instrument", width=170)
        tcmd.column("command", width=170)
        tcmd.column("parameter", width=150)
        tcmd.column("code", width=170)

        tcmd.pack(side="left", fill="both", expand=True)

        scrollY = ttk.Scrollbar(fcmd, orient="vertical", command=tcmd.yview)

        tcmd.configure(yscrollcommand=scrollY.set)

        scrollY.place(x=1234, y=0, height=1000)
        ctk.CTkLabel(self.tabview.tab(texts[2]), text="Select Method:", font=("Segoe UI", 16, "bold")).place(x=30, y=20)
        cmdMethodNames = getMethodNames()
        cbCmdMet = ctk.CTkComboBox(self.tabview.tab(texts[2]), values=cmdMethodNames, state="readonly",font=("Segoe UI", 16, "bold"),command=lambda choice: cmdLoadMethod(choice),width=160, height=30)
        cbCmdMet.place(x=160,y=20) 
        ctk.CTkLabel(self.tabview.tab(texts[2]), text="Time from start:", font=("Segoe UI", 16, "bold")).place(x=340, y=20)
        tbCmdTime =  ctk.CTkTextbox(self.tabview.tab(texts[2]), width=150, height=30,border_width=2, border_color="#1492c4")
        tbCmdTime.place(x=470, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[2]), text="state:", font=("Segoe UI", 16, "bold")).place(x=640, y=20)
        states = ["Run", "Pause", "Skip"]
        cbCmdStates = ctk.CTkComboBox(self.tabview.tab(texts[2]), width=150, height=30, values=states , state="readonly")
        cbCmdStates.place(x=690, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[2]), text="description:", font=("Segoe UI", 16, "bold")).place(x=850, y=20)
        tbCmdInfo = ctk.CTkTextbox(self.tabview.tab(texts[2]), width=340, height=30,border_width=2, border_color="#1492c4")
        tbCmdInfo.place(x=950, y=20)
        ctk.CTkLabel(self.tabview.tab(texts[2]), text="instrument:", font=("Segoe UI", 16, "bold")).place(x=30, y=80)
        cmdInsNames = getInstrumentNames()
        cbCmdIns = ctk.CTkComboBox(self.tabview.tab(texts[2]), values=cmdInsNames, state="readonly",font=("Segoe UI", 16, "bold"),width=160, height=30)
        cbCmdIns.place(x=150, y=80)
        ctk.CTkLabel(self.tabview.tab(texts[2]), text="command:", font=("Segoe UI", 16, "bold")).place(x=350, y=80)
        commands = [c[:-1] for c in getCommandsName()]
        cbCmdCommands = ctk.CTkComboBox(self.tabview.tab(texts[2]), width=150, height=30, values=commands , state="readonly", command=lambda choice: loadCmdCommands(choice))
        tbCmdParameter = ctk.CTkTextbox(self.tabview.tab(texts[2]), width=100, height=30,border_width=2, border_color="#1492c4")
        cbCmdCommands.place(x=450, y=80)

        btnCmdEditor = ctk.CTkButton(self.tabview.tab(texts[2]), height=30,width=160, command=lambda: addLine(),font=("Segoe UI", 16, "bold"), text="Add")
        btnCmdEditor.place(x=740, y=80)
        btnCmdDelete = ctk.CTkButton(self.tabview.tab(texts[2]), height=30,width=160, command=lambda: delAll(),font=("Segoe UI", 16, "bold"), text="Delete All")

        btnCmdClearSel = ctk.CTkButton(self.tabview.tab(texts[2]), height=30,width=160, command=lambda:cmdClearSel(),font=("Segoe UI", 16, "bold"), text="Clear Selection")
        btnCmdClearSel.place(x=1080, y=80)

        btnCmdCancel =  ctk.CTkButton(self.tabview.tab(texts[2]), height=30,width=160, command=lambda:cancelCmd(),font=("Segoe UI", 16, "bold"), text="Cancel")

        tbCmdTime.configure(state="disabled", border_color="#cc1a0d")
        cbCmdStates.configure(state="disabled", border_color="#cc1a0d")
        tbCmdInfo.configure(state="disabled", border_color="#cc1a0d")
        cbCmdIns.configure(state="disabled", border_color="#cc1a0d")
        cbCmdCommands.configure(state="disabled", border_color="#cc1a0d")

        def cmdClearSel():
            cbCmdMet.set("")
            btnCmdDelete.configure(text="Delete All")
            btnCmdDelete.place_forget()
            loadCmdTable()

        def cancelCmd():
            clearCmdIn()   
            btnCmdCancel.place_forget()
            lineMode["value"] = False
            tbCmdTime.configure(state="disabled", border_color="#cc1a0d")
            cbCmdStates.configure(state="disabled", border_color="#cc1a0d")
            tbCmdInfo.configure(state="disabled", border_color="#cc1a0d")
            cbCmdIns.configure(state="disabled", border_color="#cc1a0d")
            cbCmdCommands.configure(state="disabled", border_color="#cc1a0d")

        def clearCmdIn():
            tbCmdTime.delete("1.0", "end")
            cbCmdStates.set("")
            tbCmdInfo.delete("1.0", "end")
            cbCmdIns.set("")
            cbCmdCommands.set("")

        def addLine():
            global SelectedProfil
            if cbCmdMet.get() != "":
                if lineMode["value"]:
                    proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
                    if proceed:
                        lineMode["value"] = False
                        method = cbCmdMet.get()
                        info = tbCmdInfo.get("1.0", "end").strip()
                        time = tbCmdTime.get("1.0", "end").strip()
                        instrument = cbCmdIns.get()
                        command = cbCmdCommands.get()
                        par = bool(getCommandsPar(command))
                        parameter = "" 
                        if par:
                            parameter = int(tbCmdParameter.get("1.0", "end").strip())

                        code = getCommandCode(command) + str(parameter)
                        state = None 
                        if cbCmdStates.get() == "Run":
                            state = 1
                        elif cbCmdStates.get() == "Pause":
                            state = 2
                        elif cbCmdStates.get() == "Skip":
                            state = 3

                        if method and info and time and instrument and command and code and state: 
                            addCmd(method, info, time, instrument, command, parameter, code, state)
                            clearCmdIn()   
                            tbCmdTime.configure(state="disabled", border_color="#cc1a0d")
                            cbCmdStates.configure(state="disabled", border_color="#cc1a0d")
                            tbCmdInfo.configure(state="disabled", border_color="#cc1a0d")
                            cbCmdIns.configure(state="disabled", border_color="#cc1a0d")
                            cbCmdCommands.configure(state="disabled", border_color="#cc1a0d") 
                            btnEditor.configure(text="Add", command=lambda: addLine())
                            btnMetCancel.place_forget() 
                            loadCmdTable()

                        else:
                            tk.messagebox.showwarning(title="Warning", message="all inputs must be filled in to create a line")
                else:
                    lineMode["value"] = True
                    btnEditor.configure(text="Save")
                    commands = [c[:-1] for c in getCommandsNameByProfil(SelectedProfil)]
                    
                    cbCmdCommands.configure(values=commands)
                    tbCmdTime.configure(state="normal", border_color="#1492c4")
                    cbCmdStates.configure(state="normal", border_color="#1492c4")
                    tbCmdInfo.configure(state="normal", border_color="#1492c4")
                    cbCmdIns.configure(state="normal", border_color="#1492c4")
                    cbCmdCommands.configure(state="normal", border_color="#1492c4")

                    btnCmdCancel.place(x=1080,y=120)
            else:
                tk.messagebox.showwarning(title="Warning", message="Please select method when creating a line")

        def editLine():
            global SelectedProfil
            if cbCmdMet.get() != None:
                if lineMode["value"]:
                    proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
                    if proceed:
                        lineMode["value"] = False
                        method = cbCmdMet.get()
                        info = tbCmdInfo.get("1.0", "end").strip()
                        time = tbCmdTime.get("1.0", "end").strip()
                        instrument = cbCmdIns.get()
                        command = cbCmdCommands.get()
                        par = bool(getCommandsPar(command))
                        parameter = ""
                        if par:
                            parameter = int(tbCmdParameter.get("1.0", "end").strip())

                        code = getCommandCode(command) + str(parameter)
                        state = None 
                        if cbCmdStates.get() == "Run":
                            state = 1
                        elif cbCmdStates.get() == "Pause":
                            state = 2
                        elif cbCmdStates.get() == "Skip":
                            state = 3

                        if method and info and time and instrument and command and code and state: 
                            id = getCmdId()
                            if id == False:
                                tk.messagebox.showwarning(title="Warning", message="no line sellected")
                                return
                            updateCmd(method, info, time, instrument,command,parameter, code, state, id)
                            clearCmdIn()   
                            tbCmdTime.configure(state="disabled", border_color="#cc1a0d")
                            cbCmdStates.configure(state="disabled", border_color="#cc1a0d")
                            tbCmdInfo.configure(state="disabled", border_color="#cc1a0d")
                            cbCmdIns.configure(state="disabled", border_color="#cc1a0d")
                            cbCmdCommands.configure(state="disabled", border_color="#cc1a0d")
                            btnEditor.configure(text="Add", command=lambda: addLine())
                            btnCmdCancel.place_forget() 
                            loadCmdTable()

                        else:
                            tk.messagebox.showwarning(title="Warning", message="all inputs must be filled in to edit a line")
                else:
                    id = getCmdId()
                    if id == False:
                        tk.messagebox.showwarning(title="Warning", message="no line sellected")
                        return
                    lineMode["value"] = True
                    btnCmdCancel.place(x=1080, y=120)
                    tbCmdTime.configure(state="normal", border_color="#1492c4")
                    cbCmdStates.configure(state="normal", border_color="#1492c4")
                    tbCmdInfo.configure(state="normal", border_color="#1492c4")
                    cbCmdIns.configure(state="normal", border_color="#1492c4")
                    cbCmdCommands.configure(state="normal", border_color="#1492c4")
                    btnEditor.configure(text="Save")

                    commands = [c[:-1] for c in getCommandsNameByProfil(SelectedProfil)]
                    
                    cbCmdCommands.configure(values=commands)
                    row = getCmdById(id)

                    tbCmdTime.delete("1.0", "end")
                    tbCmdTime.insert("1.0", str(row[3]))
                    text = None
                    if row[8] == 1:
                        text = "Run"
                    elif row[8] == 2:
                        text = "Pause"
                    elif row[8] == 3:
                        text = "Skip"
                    cbCmdStates.set(text)
                    tbCmdInfo.delete("1.0", "end")
                    tbCmdInfo.insert("1.0", row[2])
                    cbCmdIns.set(row[4])
                    cbCmdCommands.set(row[5])
                    par = bool(getCommandsPar(row[5]))
                    if par:
                        tbCmdParameter.delete("1.0", "end")
                        tbCmdParameter.insert("1.0", row[6])
            else:
                tk.messagebox.showwarning(title="Warning", message="Please select method when editinng a line")
        def delAll():
            if cbCmdMet.get() != "":
                deleteAllCmd(cbCmdMet.get())    
                loadCmdTable()
            else:
                tk.messagebox.showwarning(title="Warning", message="You need to select method when deleting lines")

        def delSelected():
            if cbCmdMet.get() != "":
                deleteSelCmd(getCmdId())
                loadCmdTable()
            else:
                tk.messagebox.showwarning(title="Warning", message="You need to select method when deleting lines")

        def getCmdId():
            selected = tcmd.selection()

            if selected:
                values = tcmd.item(selected[0], "values")
                return values[0]
            else:
                return False

        def loadCmdCommands(choice):
            par = getCommandsPar(choice)
            if par == 1:
                tbCmdParameter.place(x=620, y=80)
            else:
                tbCmdParameter.place_forget()

        def cmdLoadMethod(choice):
            loadCmdTable()
            btnCmdDelete.place(x=910, y=80)

        def loadCmdTable():
            if cbCmdMet.get() != "":
                tcmd.delete(*tcmd.get_children())


                rows = getCmdByMethod(cbCmdMet.get().strip()) 

                for row in rows:
                    id = row[0]
                    description = row[2]
                    time = row[3]
                    instrument = row[4]
                    command = row[5]
                    parameter = row[6]
                    code = row[7]
                    state = row[8]
                    tcmd.insert("","end", values=(id, time,state,description, instrument, command, parameter,code))
            else:
                tcmd.delete(*tcmd.get_children())

        loadCmdTable()

        def tcmdChange(event):
            btnCmdEditor.configure(text="Edit", command=lambda: editLine())
            btnCmdDelete.configure(text="Delete Selected", command=lambda: delSelected())
        

        tcmd.bind("<<TreeviewSelect>>", tcmdChange)

        #--------------------------tab 4-------------------------------------------#

        @dataclass
        class sentMet:
            running: bool
            stoped: bool
            paused: bool
            currMes: int

        lines = sentMet(False, False, False, 0)

        fRun = ctk.CTkFrame(
            self.tabview.tab(texts[3]),
            width=1500,
            height=1200
        )

        fRun.place(x=30, y=240)


        columns = ("id","time", "state", "description", "instrument", "command", "parameter", "code")

        tRun = ttk.Treeview(fRun, columns=columns, show="headings", height=23)

        tRun.heading("id", text="id")
        tRun.heading("time", text="time")
        tRun.heading("state", text="state")
        tRun.heading("description", text="description")
        tRun.heading("instrument", text="instrument")
        tRun.heading("command", text="command")
        tRun.heading("parameter", text="parameter")
        tRun.heading("code", text="code")

        tRun.column("id", width=70)
        tRun.column("time", width=170)
        tRun.column("state", width=100)
        tRun.column("description", width=250)
        tRun.column("instrument", width=170)
        tRun.column("command", width=170)
        tRun.column("parameter", width=150)
        tRun.column("code", width=170)

        tRun.pack(side="left", fill="both", expand=True)

        scrollY = ttk.Scrollbar(fRun, orient="vertical", command=tcmd.yview)


        tRun.configure(yscrollcommand=scrollY.set)

        scrollY.place(x=1234, y=0, height=1000)
        tRun.bind("<Button-1>", lambda e: "break")

        ctk.CTkLabel(self.tabview.tab(texts[3]), text="Select Method:", font=("Segoe UI", 16, "bold")).place(x=30, y=20)
        runMethodNames = getMethodNames()
        cbRunMet = ctk.CTkComboBox(self.tabview.tab(texts[3]), values=runMethodNames, state="readonly",font=("Segoe UI", 16, "bold"),command=lambda choice: loadRunTable(choice),width=160, height=30)
        cbRunMet.place(x=160, y=20)

        btnStart = ctk.CTkButton(self.tabview.tab(texts[3]), height=50,width=300, command=lambda: start(),font=("Segoe UI", 16, "bold"), text="Start", text_color="#2E2E2E")
        btnStop = ctk.CTkButton(self.tabview.tab(texts[3]), height=50,width=300, command=lambda: stop(),font=("Segoe UI", 16, "bold"), text="Stop", text_color="#2E2E2E")
        btnPause = ctk.CTkButton(self.tabview.tab(texts[3]), height=50,width=300, command=lambda: pause(),font=("Segoe UI", 16, "bold"), text="Pause", text_color="#2E2E2E")
        btnReset = ctk.CTkButton(self.tabview.tab(texts[3]), height=50, width=300, command=lambda: reset(), font=("Segoe UI", 16, "bold"), text="Reset", text_color="#2E2E2E")
        btnStart.place(x=30, y=150)
        btnStop.place(x=350, y=150)
        btnPause.place(x=670, y=150)
        btnReset.place(x=990, y=150)
        btnStart.configure(fg_color="green", hover_color="darkgreen")
        btnStop.configure(fg_color="gray", state="disabled", hover_color="darkred")
        btnPause.configure(fg_color="gray", state="disabled", hover_color="#B8860B")
        btnReset.configure(fg_color="gray", state="disabled", hover_color="darkred")

        def repeat():

            self.after(1000, repeat)

        repeat()

        def start():
            lines.running = True
            lines.paused = False
            lines.stoped = False
            btnStart.configure(fg_color="gray", state="disabled", text="Start")
            btnReset.configure(fg_color="gray", state="disabled")
            btnPause.configure(fg_color="yellow", state="normal")
            btnStop.configure(fg_color="red", state="normal")
        
        def stop():
            lines.running = False
            lines.paused = False
            lines.stoped = True
            btnStart.configure(fg_color="gray", state="disabled", text="Start")
            btnPause.configure(fg_color="gray", state="disabled")   
            btnStop.configure(fg_color="gray", state="disabled")
            btnReset.configure(fg_color="red", state="normal")
                
        def pause():
            lines.running = False
            lines.paused = True
            lines.stoped = False
            btnStart.configure(fg_color="green", state="normal", text="Resume")
            btnPause.configure(fg_color="gray", state="disabled")            
            btnStop.configure(fg_color="red", state="normal")
            btnReset.configure(fg_color="gray", state="disabled")
        
        def reset():
            btnStart.configure(fg_color="green", hover_color="darkgreen", state="normal")
            btnStop.configure(fg_color="gray", state="disabled", hover_color="darkred")
            btnPause.configure(fg_color="gray", state="disabled", hover_color="#B8860B")
            btnReset.configure(fg_color="gray", state="disabled", hover_color="darkred")

        def loadRunTable(choice):
            if cbRunMet.get() != "":
                tRun.delete(*tRun.get_children())

                rows = getCmdByMethod(cbRunMet.get().strip()) 

                for row in rows:
                    id = row[0]
                    description = row[2]
                    time = row[3]
                    instrument = row[4]
                    command = row[5]
                    parameter = row[6]
                    code = row[7]
                    state = row[8]
                    tRun.insert("","end", values=(id, time,state,description, instrument, command, parameter,code))
            else:
                tRun.delete(*tRun.get_children())
 

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
        ctk.CTkLabel(pref, text="Timeout if arduino won't answer", font=("Segoe UI", 16, "bold")).place(x=30, y=90)

        timeout = config.getboolean("program", "timeout")
        TOSwitch = ctk.CTkSwitch(inner, text="")
        if timeout:
            TOSwitch.select()
        else:
            TOSwitch.deselect()

        TOSwitch.place(x=420, y=90)

        ctk.CTkLabel(pref, text="Clear selection after edit in profile", font=("Segoe UI", 16, "bold")).place(x=30, y=130)

        ClearIn = config.getboolean("program", "ClearProfilSelection")
        InSwitch = ctk.CTkSwitch(inner, text="")
        if ClearIn:
            InSwitch.select()
        else:
            InSwitch.deselect()

        InSwitch.place(x=420, y=130)

        ctk.CTkButton(inner, text="Confirm", command=lambda: self.btnCon(pref, TOSwitch, InSwitch), width=200).place(x=260, y=330)
        ctk.CTkButton(inner, text="Cancel", command=lambda: pref.destroy(), width=200).place(x=30, y=330)




    def reloadCom(self, Tcomand):
        Tcomand.delete(*Tcomand.get_children())

        rows = getCommands()

        for row in rows:
            name = row[1]
            code = row[2]
            parameter = row[3]
            info = row[4]
            profil = row[5]
            Tcomand.insert("","end", values=(name, code, parameter, info, profil))


    def addInstrument(self):
        mode = {"value": False}
        wIns = ctk.CTkToplevel(self)
        wIns.geometry("900x610+400+200")
        wIns.overrideredirect(True)
        wIns.configure(fg_color=("#f0f0f0","#1c1c1c"), corner_radius=50)   
        outer = ctk.CTkFrame(wIns, fg_color=("#1c1c1c", "#f0f0f0"), corner_radius=3)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        inner = ctk.CTkFrame(outer, fg_color=("#f0f0f0","#1c1c1c"), corner_radius=4)
        inner.pack(fill="both", expand=True, padx=2, pady=2)          
        ctk.CTkLabel(wIns, text="Add Instrument", font=("Helvetica", 46, "bold")).place(x=30, y=20)    

        tIns = ttk.Treeview(
            wIns,
            columns=("Name", "Address"),
            show="headings"
        )

        tIns.heading("Name", text="Name")
        tIns.heading("Address", text="Address")
        tIns.place(x=20, y=100, width=850, height=300)
        
        scrollbar = ttk.Scrollbar(wIns, orient="vertical", command=tIns.yview)
        tIns.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=852, y=101, height=298)
        ctk.CTkButton(wIns, font=("Helvetica", 20 ,"bold"), text="X", command=lambda: wIns.destroy(), width=30, height=30, text_color=("black", "white"), border_width=2, border_color=("black","white") ,fg_color="transparent", hover_color="grey", corner_radius=15).place(x=810, y=37)

        ctk.CTkLabel(wIns, text="name:", font=("Segoe UI", 16, "bold")).place(x=30, y=420)
        tbInsName =  ctk.CTkTextbox(wIns, width=260, height=30,border_width=2, border_color="#1492c4")
        ctk.CTkLabel(wIns, text="address:", font=("Segoe UI", 16, "bold")).place(x=500, y=420)
        tbInsAddr =  ctk.CTkTextbox(wIns, width=260, height=30,border_width=2, border_color="#1492c4")
        tbInsName.place(x=110, y=420)
        tbInsAddr.place(x=590, y=420)

        btnInsEditor = ctk.CTkButton(wIns,width=400,  height=30, command=lambda: newInstrument(),font=("Segoe UI", 16, "bold"), text="New")
        btnInsDelete = ctk.CTkButton(wIns,width=400,  height=30, command=lambda: deleteIns(),font=("Segoe UI", 16, "bold"), text="Delete all")
        btnInsClear = ctk.CTkButton(wIns,width=830,  height=30, command=lambda: clearSelIns(),font=("Segoe UI", 16, "bold"), text="Clear selection")
        btnInsEditor.place(x=30, y=470)
        btnInsDelete.place(x=460, y=470)
        btnInsClear.place(x=30, y=510)
        tbInsName.configure(state="disabled", border_color="#cc1a0d")
        tbInsAddr.configure(state="disabled", border_color="#cc1a0d")
        btnInsCancel = ctk.CTkButton(wIns,width=830,  height=30, command=lambda: cancelIns(),font=("Segoe UI", 16, "bold"), text="Cancel")

        def cancelIns():
            clearInsInput()
            tbInsName.configure(state="disabled", border_color="#cc1a0d")
            tbInsAddr.configure(state="disabled", border_color="#cc1a0d")
            btnInsCancel.place_forget()
            mode["value"] = False
            btnInsEditor.configure(
                text="New",
                command=newInstrument
            )
            tIns.selection_remove(tIns.selection())


        def loadTIns():
            tIns.delete(*tIns.get_children())
            rows = getInstruments()

            for row in rows:
                name = row[1]
                addr = row[2]
                tIns.insert("","end", values=(name, addr))
        loadTIns()

        def deleteSelIns():
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede", parent=wIns)
            if proceed:
                selectedItem = tIns.selection()
                if not selectedItem:
                    return

                vals = tIns.item(selectedItem[0], "values")
                name = vals[0]
                deleteInstrument(name)
                loadTIns()
                clearInsInput()

        def editIns():
            if mode["value"]:
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede", parent=wIns)
                if proceed:
                    mode["value"] = False
                    Iname = tbInsName.get("1.0", "end").strip()
                    Iaddr = tbInsAddr.get("1.0", "end").strip()
                    if countInstrument(Iname) < 2:
                        if Iname and Iaddr:
                            selectedItem = tIns.selection()
                            if not selectedItem:
                                return

                            vals = tIns.item(selectedItem[0], "values")
                            name = vals[0]
                            id = getInstrumentId(name)
                            updateInstrument(Iname, Iaddr, id)
                            loadTIns()
                            clearInsInput()
                            btnInsEditor.configure(
                                text="New",
                                command=newInstrument
                            )
                            tbInsName.configure(state="disabled", border_color="#cc1a0d")
                            tbInsAddr.configure(state="disabled", border_color="#cc1a0d")
                            btnInsCancel.place_forget()
                        else:
                            tk.messagebox.showwarning(title="warning", message="You must fill all of the information when editing a command", parent=wIns)
                    else:
                        tk.messagebox.showerror(title="Error", message="Two Commands can't have same names!", parent=wIns)
                else:
                    return
            else:
                mode["value"] = True
                btnInsEditor.configure(text="Save")
                tbInsName.configure(state="normal", border_color="#1492c4")
                tbInsAddr.configure(state="normal", border_color="#1492c4")
                selectedItem = tIns.selection()
                if not selectedItem:
                    return
                
                btnInsCancel.place(x=30, y=550)
                
                vals = tIns.item(selectedItem[0], "values")

                if vals:
                    tbInsName.delete("1.0", "end")
                    tbInsAddr.delete("1.0","end")
                    tbInsName.insert("1.0", vals[0])
                    tbInsAddr.insert("1.0", vals[1])

        def clearSelIns():
            btnInsDelete.configure(text="Delete All", command=lambda: deleteIns())
            btnInsEditor.configure(text="New", command= lambda: newInstrument())
            tIns.selection_remove(tIns.selection())                            
            clearInsInput()

        def deleteIns():
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede", parent=wIns)
            if proceed:
                clearInstrument()
                loadTIns()
                clearInsInput()

        def clearInsInput():
            tbInsName.delete("1.0", "end")
            tbInsName.insert("1.0", "")
            tbInsAddr.delete("1.0", "end")
            tbInsAddr.insert("1.0", "")

        def newInstrument():
            if mode["value"]:
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede", parent=wIns)
                if proceed:
                    mode["value"] = False
                    Iname = tbInsName.get("1.0", "end").strip()
                    Iaddr = tbInsAddr.get("1.0", "end").strip()
                    if countInstrument(Iname) == 0:
                        if Iname and Iaddr:
                            addInstument(Iname, Iaddr)
                            loadTIns()
                            clearInsInput()
                            btnInsEditor.configure(
                                text="New",
                                command=newInstrument
                            )
                            tbInsName.configure(state="disabled", border_color="#cc1a0d")
                            tbInsAddr.configure(state="disabled", border_color="#cc1a0d")
                            btnInsCancel.place_forget()
                        else:
                            tk.messagebox.showwarning(title="warning", message="You must fill all of the information when creating a command", parent=wIns)
                    else:
                        tk.messagebox.showerror(title="Error", message="Two Commands can't have same names!", parent=wIns)
                else:
                    return
            else:
                btnInsCancel.place(x=30, y=550)
                mode["value"] = True
                btnInsEditor.configure(text="Save")
                tbInsName.configure(state="normal", border_color="#1492c4")
                tbInsAddr.configure(state="normal", border_color="#1492c4")

        def tInsChange(event):

            selectedItem = tIns.selection()
            if not selectedItem:
                return
            
            btnInsDelete.configure(text="Delete selected", command=lambda: deleteSelIns())
            btnInsEditor.configure(text="edit", command=lambda: editIns())

            vals = tIns.item(selectedItem[0], "values")

            if vals:
                tbInsName.delete("1.0", "end")
                tbInsAddr.delete("1.0","end")
                tbInsName.insert("1.0", vals[0])
                tbInsAddr.insert("1.0", vals[1])

        tIns.bind("<<TreeviewSelect>>", tInsChange)

    def addCom(self):
        EditMode = {"value": False}

        self.currentId = -1
        
        wadd = ctk.CTkToplevel(self)
        wadd.geometry("900x710+400+200")
        wadd.overrideredirect(True)
        wadd.configure(fg_color=("#f0f0f0","#1c1c1c"), corner_radius=50)   
        outer = ctk.CTkFrame(wadd, fg_color=("#1c1c1c", "#f0f0f0"), corner_radius=3)
        outer.pack(fill="both", expand=True, padx=4, pady=4)

        inner = ctk.CTkFrame(outer, fg_color=("#f0f0f0","#1c1c1c"), corner_radius=4)
        inner.pack(fill="both", expand=True, padx=2, pady=2)          
        ctk.CTkLabel(wadd, text="add commands", font=("Helvetica", 46, "bold")).place(x=30, y=20)

        Tcomand = ttk.Treeview(
            wadd,
            columns=("name", "code", "parameter", "info", "profil"),
            show="headings"
        )

        Tcomand.heading("name", text="name")
        Tcomand.heading("code", text="code")
        Tcomand.heading("parameter", text="parameter")
        Tcomand.heading("info", text="info")
        Tcomand.heading("profil", text="profil")

        Tcomand.column("name", width=100, anchor="center")
        Tcomand.column("code", width=50, anchor="center")
        Tcomand.column("parameter", width=100, anchor="center")
        Tcomand.column("info", width=150, anchor="center")
        Tcomand.column("profil", width=100, anchor="center")

        self.reloadCom(Tcomand)

        def Tchange(event):
            selectedItem = Tcomand.selection()
            if not selectedItem:
                return

            btnNew.configure(text="Edit", command=lambda: editCommand(EditMode))
            btnDelete.configure(text="Delete Selected", command=lambda: deleteSelected())     

            codeValues = Tcomand.item(selectedItem[0], "values")
            if codeValues:
                self.currentId = getCommandsId(codeValues[0])
                
                tbComName.delete("1.0", "end")
                tbComName.insert("1.0", codeValues[0])
                
                tbCode.delete("1.0", "end")
                tbCode.insert("1.0", codeValues[1])
                
                if int(codeValues[2]):
                    swPar.select()
                else:
                    swPar.deselect()
                    
                tbinfo.delete("1.0", "end")
                tbinfo.insert("1.0", codeValues[3]) 

        Tcomand.bind("<<TreeviewSelect>>", Tchange)
        Tcomand.place(x=20, y=100, width=850, height=300)
        
        scrollbar = ttk.Scrollbar(wadd, orient="vertical", command=Tcomand.yview)
        Tcomand.configure(yscrollcommand=scrollbar.set)
        scrollbar.place(x=852, y=101, height=298)
        
        ctk.CTkButton(wadd, font=("Helvetica", 20 ,"bold"), text="X", command=lambda: closeWin(), width=30, height=30, text_color=("black", "white"), border_width=2, border_color=("black","white") ,fg_color="transparent", hover_color="grey", corner_radius=15).place(x=810, y=37)
        
        def closeWin():
            wadd.destroy()

        ctk.CTkLabel(wadd, text="name: ", font=("Segoe UI", 16, "bold")).place(x=70, y=420)
        tbComName = ctk.CTkTextbox(wadd, width=200, height=20, border_width=2, border_color="#1492c4")
        tbComName.place(x=140, y=420) 
        
        ctk.CTkLabel(wadd, text="code: ", font=("Segoe UI", 16, "bold")).place(x=380, y=420)
        tbCode = ctk.CTkTextbox(wadd, width=200, height=20, border_width=2, border_color="#1492c4")
        tbCode.place(x=440, y=420) 
        
        ctk.CTkLabel(wadd, text="parameter: ", font=("Segoe UI", 16, "bold")).place(x=680, y=420)
        swPar = ctk.CTkSwitch(wadd, text="")
        swPar.place(x= 780, y=423)
        
        ctk.CTkLabel(wadd, text="info: ", font=("Segoe UI", 16, "bold")).place(x=50, y=470)
        tbinfo = ctk.CTkTextbox(wadd, width=470, height=20, border_width=2, border_color="#1492c4")
        tbinfo.place(x=100, y=470)
        ctk.CTkLabel(wadd, text="profil: ", font=("Segoe UI", 16, "bold")).place(x=600, y=470)
        profiles = getProfilName()
        cbProfil = ctk.CTkComboBox(wadd, width=180, height=30, values=profiles, state="readonly")
        cbProfil.place(x=660, y=470)


        tbComName.configure(state="disabled",  border_color="#cc1a0d") 
        tbCode.configure(state="disabled", border_color="#cc1a0d")
        swPar.configure(state="disabled", border_color="#cc1a0d")
        tbinfo.configure(state="disabled", border_color="#cc1a0d")
        cbProfil.configure(state="disabled", border_color="#cc1a0d")
        
        btnDelete = ctk.CTkButton(wadd, text="Delete All", font=("Segoe UI", 16, "bold"), command=lambda: deleteAll(), width=370, text_color_disabled="white", fg_color="red", hover_color="#610000", text_color="white")
        btnDelete.place(x=65, y=520)
        
        btnNew = ctk.CTkButton(wadd, text="New", font=("Segoe UI", 16, "bold"), command=lambda: newCommand(EditMode), width=370, state="normal", text_color_disabled="white", fg_color="green", hover_color="#00610d", text_color="white")
        btnNew.place(x=465, y=520)
        
        btnClearCom = ctk.CTkButton(wadd, text="clear selection", font=("Segoe UI", 16, "bold"), command=lambda: clearCom(), width=770)
        btnClearCom.place(x=65, y=560)

        btnComCancel = ctk.CTkButton(wadd, text="Cancel", font=("Segoe UI", 16, "bold"), command=lambda: ComCancel(), width=370)

        def ComCancel():
            EditMode["value"] = False
            btnNew.configure(text="New")
            clearCom()

            tbComName.configure(state="disabled",  border_color="#cc1a0d") 
            tbCode.configure(state="disabled", border_color="#cc1a0d")
            swPar.configure(state="disabled", border_color="#cc1a0d")
            tbinfo.configure(state="disabled", border_color="#cc1a0d")
            cbProfil.configure(state="disabled", border_color="#cc1a0d")
            btnComCancel.place_forget()
            btnClearCom.configure(width=770)

        def clearCom():
            Tcomand.selection_remove(Tcomand.selection())
            clearTb()
            btnNew.configure(text="New", command=lambda: newCommand(EditMode))
            btnDelete.configure(text="Delete All", command=lambda: deleteAll())             
    
        def deleteAll():
            delete = messagebox.askquestion("Warning", "Are you sure?", parent=wadd) 
            if delete == 'yes': 
                clearCommands()
                self.reloadCom(Tcomand)
                clearCom()

        def editCommand(EditMode):
            if EditMode["value"]:
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceed?", parent=wadd)
                if proceed:
                    Fname = tbComName.get("1.0", "end").strip()
                    Fcode = tbCode.get("1.0", "end").strip()
                    Finfo = tbinfo.get("1.0", "end").strip()    
                    Fprofil = cbProfil.get().strip()
                    EditMode["value"] = False
                    if Fname and Fcode and Finfo and Fprofil:
                        codeValues = Tcomand.item(Tcomand.selection()[0], "values")

                        updateCommands(Fname, Fcode, swPar.get(), Finfo, Fprofil, self.currentId)

                        if commandsCountByName(Fname) > 1:
                            updateCommands(codeValues[0], codeValues[1], codeValues[2], codeValues[3], self.currentId) 
                            tk.messagebox.showerror(title="Error", message="Two Commands can't have same names!", parent=wadd)
                            return
                        
                        self.reloadCom(Tcomand)
                        tk.messagebox.showinfo("Success", "Database updated successfully", parent=wadd)
                        clearCom()
                        btnNew.configure(text="New")

                        tbComName.configure(state="disabled",  border_color="#cc1a0d") 
                        tbCode.configure(state="disabled", border_color="#cc1a0d")
                        swPar.configure(state="disabled", border_color="#cc1a0d")
                        tbinfo.configure(state="disabled", border_color="#cc1a0d")
                        btnComCancel.place_forget()
                        btnClearCom.configure(width=770)
                    else:
                        tk.messagebox.showwarning(title="Warning", message="You must fill all of the information when creating a command", parent=wadd)
            else:
                EditMode["value"] = True
                tbComName.configure(state="normal",  border_color="#1492c4") 
                tbCode.configure(state="normal", border_color="#1492c4")
                swPar.configure(state="normal", border_color="#1492c4")
                tbinfo.configure(state="normal", border_color="#1492c4")
                cbProfil.configure(state="normal", border_color="#1492c4")
                btnNew.configure(text="Save")
                btnClearCom.configure(width=370)
                btnComCancel.place(x=465, y=560)
                selectedItem = Tcomand.selection()
                if not selectedItem:
                    return

                codeValues = Tcomand.item(selectedItem[0], "values")
                if codeValues:
                    self.currentId = getCommandsId(codeValues[0])
                    
                    tbComName.delete("1.0", "end")
                    tbComName.insert("1.0", codeValues[0])
                    
                    tbCode.delete("1.0", "end")
                    tbCode.insert("1.0", codeValues[1])
                    
                    if int(codeValues[2]):
                        swPar.select()
                    else:
                        swPar.deselect()
                        
                    tbinfo.delete("1.0", "end")
                    tbinfo.insert("1.0", codeValues[3]) 
                    cbProfil.set(codeValues[4])


         
        def newCommand(mode):
            if mode["value"]:
                btnNew.configure(text="New")
                proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede", parent=wadd)
                if proceed:
                    Fname = tbComName.get("1.0", "end").strip()
                    Fcode = tbCode.get("1.0", "end").strip()
                    Finfo = tbinfo.get("1.0", "end").strip()    
                    Fprofil = cbProfil.get().strip()
                    mode["value"] = False
                    if commandsCountByName(Fname) == 0:
                        if Fname and Fcode and Finfo and Fprofil:
                            addCommands(Fname,Fcode, swPar.get(), Finfo, Fprofil)
                            self.reloadCom(Tcomand)
                            clearTb()
                            tbComName.configure(state="disabled",  border_color="#cc1a0d") 
                            tbCode.configure(state="disabled", border_color="#cc1a0d")
                            swPar.configure(state="disabled", border_color="#cc1a0d")
                            tbinfo.configure(state="disabled", border_color="#cc1a0d")
                            cbProfil.configure(state="disabled", border_color="#cc1a0d")
                            btnClearCom.configure(width=770)
                            btnComCancel.place_forget()
                        else:
                            tk.messagebox.showwarning(title="warning", message="You must fill all of the information when creating a command", parent=wadd)
                    else:
                        tk.messagebox.showerror(title="Error", message="Two Commands can't have same names!")
                else:
                    return
            else:
                mode["value"] = True
                tbComName.configure(state="normal",  border_color="#1492c4") 
                tbCode.configure(state="normal", border_color="#1492c4")
                swPar.configure(state="normal", border_color="#1492c4")
                tbinfo.configure(state="normal", border_color="#1492c4")       
                cbProfil.configure(state="normal", border_color="#1492c4")       
                btnClearCom.configure(width=370)
                btnComCancel.place(x=465, y=560)
                btnNew.configure(text="Save")

        def clearTb():
            tbComName.delete("1.0", "end")
            tbCode.delete("1.0", "end")
            tbinfo.delete("1.0", "end")
            swPar.deselect()
            cbProfil.set("")

        def deleteSelected():
            if self.currentId != -1:
                confirm = messagebox.askyesno("Confirm Delete", "Are you sure?", parent=wadd)
                if confirm: 
                    deleteCommand(self.currentId)
                    self.reloadCom(Tcomand)
                    clearCom()
    


    def buildUi(self):
        global currentMode

        toolbar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=("#e0e0e0", "#1e1e1e"))
        toolbar.pack(side="top", fill="x")
        toolbar.pack_propagate(False)

        self.file_menu = StableDropdown(self)
        
        self.file_menu.add_separator()
        self.file_menu.add_action("add Commands", command=lambda: self.addCom())
        self.file_menu.add_action("add Instrument", command=lambda: self.addInstrument())
        self.file_menu.add_action("Preferences",  command=lambda: self.preferences())
        self.file_menu.add_separator()
        self.file_menu.add_action("Quit", command=lambda: self.quit)

        
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