import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image
import configparser
from serial.tools import list_ports
from databaze.db import *
from arduino.arduino import *

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
    global texts
    def __init__(self, master=None):
        super().__init__(master, fg_color="transparent")
        self.master = master
        
        self.pack(fill="both", expand=True)
        
        self.master.title("Control Panel | Arduino disconnected")
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
        #--------------------------tab 1------------------------------------------------#
        baudRates = ["300","1200","2400","4800","9600","19200","38400","57600","115200","230400","460800","921600",]
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Select your device profile: ",font=("Segoe UI", 16, "bold")).place(x=30,y=20)
        profilNames = getProfilName()
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
        tbTimeout = ctk.CTkTextbox(self.tabview.tab(texts[0]), width=180, height=20,border_width=2, border_color="#1492c4")
        tbTimeout.place(x=120, y=80)
        ctk.CTkLabel(self.tabview.tab(texts[0]), text="Test command: ", font=("Segoe UI", 16, "bold")).place(x=350, y=80)
        cbCommands = ctk.CTkComboBox(self.tabview.tab(texts[0]), width=180, height=30, values=getCommandsName(), state="readonly")
        cbCommands.place(x=510, y=80)

        btnEditor = ctk.CTkButton(self.tabview.tab(texts[0]),width=160,  height=30, command=lambda: newProfil(),font=("Segoe UI", 16, "bold"), text="New")
        btnDelete = ctk.CTkButton(self.tabview.tab(texts[0]),width=160, height=30, command=lambda: delAllProfils(),font=("Segoe UI", 16, "bold"), text="Delete all")
        btnClear = ctk.CTkButton(self.tabview.tab(texts[0]), height=30,width=160, command=lambda: clearProf(),font=("Segoe UI", 16, "bold"), text="Clear Selection")
        conn = True
        btnConnect = ctk.CTkButton(self.tabview.tab(texts[0]), width=650, height=40, text="Connect",font=("Segoe UI", 16, "bold"), command=lambda: arduinoConnect())

        btnDelete.place(x=930, y=80)
        btnEditor.place(x=730, y=80)

        def arduinoConnect():
            if conn:
                profil = getProfilByName(cbProfil.get())
                connection = arduino(profil[2], profil[3], profil[4])
                y = connection.connectToArduino()
                if y:         
                    ctk.CTkLabel(self.tabview.tab(texts[0]), text="Test Cmd result: ", font=("Segoe UI", 16, "bold")).place(x=750, y=145)
                    tbRes = ctk.CTkTextbox(self.tabview.tab(texts[0]), state="disabled", width=410, height=30,border_width=2, border_color="#1492c4")
                    tbRes.place(x=900, y=145)
                    self.master.title("Control Panel | Arduino connected")
                    reply = connection.send(profil[5])
                    tbRes.configure(state="normal")
                    tbRes.delete("1.0", "end")
                    tbRes.insert("1.0", reply)
                    tbRes.configure(state="disabled")

                else:
                    tk.messagebox.showwarning("Warning", "Did not find arduino")
    
        def loadProfil(choice):
            profil = getProfilByName(choice)
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
            clearProfil()
            clearInputs()
            cbProfil.configure(values=getProfilName())



        def editProfil():
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede? \nBy editing you will delete testCmd result")
            if proceed:
                id = getProfilId(cbProfil.get())
                Pname = tbName.get("1.0", "end").strip()
                Pport = cbPorts.get()
                Pbaud = int(cbBaudRate.get())
                Pcommand = cbCommands.get()
                Ptimeout = float(tbTimeout.get("1.0", "end").strip())
                if Pname and Ptimeout and Pport and Pbaud and Pcommand:
                    if countProfilByName(Pname) < 2:
                        updateProfil(Pname, Pport, Pbaud, Ptimeout,Pcommand, id)
                        clearInputs()
                        cbProfil.configure(values=getProfilName())

        def delProfil():
            if cbProfil.get():
                deleteProfil(cbProfil.get())
                clearInputs()
                cbProfil.configure(values=getProfilName())

        def newProfil():
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceede")
            if proceed:
                Pname = tbName.get("1.0", "end").strip()
                Pport = cbPorts.get()
                Pbaud = cbBaudRate.get()
                Pcommand = cbCommands.get()
                Ptimeout = tbTimeout.get("1.0", "end").strip()
                if Pname and Ptimeout and Pport and Pbaud and Pcommand:
                    if countProfilByName(Pname) < 1:
                        addProfil(Pname, Pport, Pbaud, Ptimeout, Pcommand)
                        profilNames = getProfilName()
                        cbProfil.configure(values=profilNames)
                        clearInputs()
                else:
                    tk.messagebox.showwarning(title="Warning", message="all inputs must be filled in to create a profile")

        def clearProf():
            clearInputs()
            btnEditor.configure(text="New", command=lambda: newProfil())       
            btnDelete.configure(text="Delete all", command=lambda: delAllProfils())
            btnConnect.place_forget()
            btnClear.place_forget()

        def clearInputs():
            cbCommands.set("")
            cbBaudRate.set("")
            cbPorts.set("")
            cbProfil.set("")
            tbTimeout.delete("1.0", "end")
            tbName.delete("1.0", "end")

            btnClear.place_forget()

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
            if commandsCountByName(Fname) == 0:
                if Fname and Fcode and Finfo :
                    addCommands(Fname,Fcode, par.get(), Finfo)
                    self.reloadCom(Tcomand)
                else:
                    tk.messagebox.showwarning(title="warning", message="You must fill all of the information when creating a command", parent=wadd)
            else:
                tk.messagebox.showerror(title="Error", message="Two Commands can't have same names!")
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
        self.currentId = -1
        
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

        self.reloadCom(Tcomand)

        def Tchange(event):
            selectedItem = Tcomand.selection()
            if not selectedItem:
                return

            btnNew.configure(text="Edit", command=lambda: editCommand())
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
        tbinfo = ctk.CTkTextbox(wadd, width=740, height=20, border_width=2, border_color="#1492c4")
        tbinfo.place(x=100, y=470) 
        
        btnDelete = ctk.CTkButton(wadd, text="Delete All", font=("Segoe UI", 16, "bold"), command=lambda: deleteAll(), width=370, text_color_disabled="white", fg_color="red", hover_color="#610000", text_color="white")
        btnDelete.place(x=65, y=520)
        
        btnNew = ctk.CTkButton(wadd, text="New", font=("Segoe UI", 16, "bold"), command=lambda: self.newCommand(tbComName, tbCode, swPar, tbinfo, Tcomand, wadd), width=370, state="normal", text_color_disabled="white", fg_color="green", hover_color="#00610d", text_color="white")
        btnNew.place(x=465, y=520)
        
        ctk.CTkButton(wadd, text="clear selection", font=("Segoe UI", 16, "bold"), command=lambda: clearCom(), width=770).place(x=65, y=560)

        def clearCom():
            Tcomand.selection_remove(Tcomand.selection())
            clearTb()
            btnNew.configure(text="New", command=lambda: self.newCommand(tbComName, tbCode, swPar, tbinfo, Tcomand, wadd))
            btnDelete.configure(text="Delete All", command=lambda: deleteAll())             
    
        def deleteAll():
            delete = messagebox.askquestion("Warning", "Are you sure?", parent=wadd) 
            if delete == 'yes': 
                clearCommands()
                self.reloadCom(Tcomand)
                clearCom()

        def editCommand():
            proceed = tk.messagebox.askyesno(title="Warning", message="Do you wish to proceed?", parent=wadd)
            if proceed:
                Fname = tbComName.get("1.0", "end").strip()
                Fcode = tbCode.get("1.0", "end").strip()
                Finfo = tbinfo.get("1.0", "end").strip()    
                
                if Fname and Fcode and Finfo:
                    codeValues = Tcomand.item(Tcomand.selection()[0], "values")

                    updateCommands(Fname, Fcode, swPar.get(), Finfo, self.currentId)

                    if commandsCountByName(Fname) > 1:
                        updateCommands(codeValues[0], codeValues[1], codeValues[2], codeValues[3], self.currentId) 
                        tk.messagebox.showerror(title="Error", message="Two Commands can't have same names!", parent=wadd)
                        return
                    
                    self.reloadCom(Tcomand)
                    tk.messagebox.showinfo("Success", "Database updated successfully", parent=wadd)
                    clearCom()           
                else:
                    tk.messagebox.showwarning(title="Warning", message="You must fill all of the information when creating a command", parent=wadd)

        def clearTb():
            tbComName.delete("1.0", "end")
            tbCode.delete("1.0", "end")
            tbinfo.delete("1.0", "end")
            swPar.deselect()

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