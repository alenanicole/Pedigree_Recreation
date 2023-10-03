import xml.etree.ElementTree as ET
import customtkinter as ct
from tkinter import filedialog

class Frame(ct.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

def create_app():
        app = ct.CTk()
        ct.set_appearance_mode("dark") 
        app.title("Pedigree Recreation")
        app.geometry("500x400")
        return app

def switchCode(code):
    if code == "NMTH":
        return "Mother -- "
    elif code == "NFTH":
        return "Father -- "
    elif code == "MGRMTH":
        return "Maternal Grandmother -- "
    elif code == "MGRFTH":
        return "Maternal Grandfather -- "
    elif code == "PGRMTH":
        return "Paternal Grandmother -- "
    elif code == "PGRFTH":
        return "Paternal Grandfather -- "
    elif code == "DAU":
        return "Daughter -- "
    
def validateName(given, family):
    temp = ""

    if str(given) != "None":
        temp += str(given + " ")
    
    if str(family) != "None":
        temp += str(family)

    return temp
    
def upload_file():
    file= filedialog.askopenfilename(title="Select the original patient's file", filetypes=([("XML Files","*.xml")]))
    tree = ET.parse(file)
    root = tree.getroot()
    for relative in tree.findall('.//relative'):
        code = relative.find('code')
        codeText = code.get('code')
        relationshipHolder = relative.find('relationshipHolder')
        name = relationshipHolder.find('name')
        if(name):
            given = name.find('given').text
            family = name.find('family').text
            relativeData = ""
            relativeData += switchCode(codeText)
            relativeData += validateName(given, family)
            relatives.append(relativeData)
    output_family()
            

def output_family():
    change_to_choose_patient()
    radio_var = ct.IntVar(value=0)
    i = 0
    for relativeData in relatives:
        radioButton = ct.CTkRadioButton(master=choose_patient, text=relativeData, variable=radio_var, value = i)
        radioButton.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="w")
        i += 1

    button = ct.CTkButton(master=choose_patient, text="Choose Patient", command=add_data)
    button.grid(row=i, column=0, padx=20, pady=20)

def add_data():
    print('adding info')

def reorient_file():
    print("rearranging")


def change_to_upload():
    upload.pack(fill='both', expand=1)
    button = ct.CTkButton(master=upload, text="Upload File", command=upload_file)
    button.grid(row=0, column=0, padx=20, pady=100)
    choose_patient.pack_forget()
    download.pack_forget()

def change_to_choose_patient():
    choose_patient.pack(fill='both', expand=1)
    upload.pack_forget()
    download.pack_forget()

def change_to_download():
    download.pack(fill='both', expand=1)
    choose_patient.pack_forget()
    upload.pack_forget()

relatives = []
app = create_app()
upload = Frame(app)
choose_patient = Frame(app)
download = Frame(app)
change_to_upload()
app.mainloop()