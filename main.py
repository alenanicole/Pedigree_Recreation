import xml.etree.ElementTree as ET
import customtkinter as ct
from tkinter import filedialog
from datetime import *
import time

class Frame(ct.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

def create_app():
        app = ct.CTk()
        ct.set_appearance_mode("dark") 
        app.title("Pedigree Recreation")
        app.geometry("600x400")
        app.grid_rowconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=1)
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
    
    return str(code)
    
def validateName(given, family):
    temp = ""

    if str(given) != "None":
        temp += str(given + " ")
    
    if str(family) != "None":
        temp += str(family)

    return temp
    
def upload_file():
    numOfMoth = 0
    numOfFath = 0
    file= filedialog.askopenfilename(title="Select the original patient's file", filetypes=([("XML Files","*.xml")]))
    tree = ET.parse(file)
    root = tree.getroot()
    for relative in tree.findall('.//relative'):
        code = relative.find('code')
        codeText = code.get('code')
        if(str(codeText) != "NMTH"):
            numOfMoth += 1
        if( str(codeText) != "NFTH"):
            numOfFath += 1
        relationshipHolder = relative.find('relationshipHolder')
        name = relationshipHolder.find('name')
        if(name):
            given = name.find('given').text
            family = name.find('family').text
            relativeData = ""
            relativeData += switchCode(codeText)
            relativeData += validateName(given, family)
            relatives.append(relativeData)
        elif((numOfMoth != 0 and str(codeText) != "NMTH") and (numOfFath != 0 and str(codeText) != "NFTH")):
            relativeData = ""
            relativeData += switchCode(codeText)
            relatives.append(relativeData)
    output_family()
            

def output_family():
    change_to_choose_patient()
    radio_var = ct.IntVar(value=0)
    i = 0
    for relativeData in relatives:
        radioButton = ct.CTkRadioButton(master=choose_patient, text=relativeData, variable=radio_var, value = i)
        radioButton.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="ew")
        i += 1

    button = ct.CTkButton(master=choose_patient, text="Choose Patient", command= lambda: add_data(radio_var.get()))
    button.grid(row=i, column=0, padx=20, pady=20)

def add_data(idx):
    change_to_add_patient()
    first_name = ct.StringVar()
    last_name = ct.StringVar()
    dob = ct.StringVar()
    mrn = ct.StringVar()
    new_patient_label = ct.CTkLabel(master=add_patient_info, text = "New patient: " + relatives[idx])
    new_patient_label.grid(row=0, column=1, padx=20, pady=(10, 0), sticky="w")
    first_name_label = ct.CTkLabel(master=add_patient_info, text = "First Name")
    first_name_label.grid(row = 1, column = 0, padx=20, pady=(10, 0), sticky="w")
    last_name_label = ct.CTkLabel(master=add_patient_info, text = "Last Name")
    last_name_label.grid(row = 2, column = 0, padx=20, pady=(10, 0), sticky="w")
    dob_label = ct.CTkLabel(master=add_patient_info, text = "Date of Birth (YYYYMMDD)")
    dob_label.grid(row = 3, column = 0, padx=20, pady=(10, 0), sticky="w")
    mrn_label =  ct.CTkLabel(master=add_patient_info, text = "Medical Record Number")
    mrn_label.grid(row = 4, column = 0, padx=20, pady=(10, 0), sticky="w")
    first_name_entry = ct.CTkEntry(master=add_patient_info, textvariable=first_name)
    first_name_entry.grid(row = 1, column = 1, padx=20, pady=(10, 0), sticky="nsew")
    last_name_entry = ct.CTkEntry(master=add_patient_info, textvariable=last_name)
    last_name_entry.grid(row = 2, column = 1, padx=20, pady=(10, 0), sticky="nsew")
    dob_entry = ct.CTkEntry(master=add_patient_info, textvariable=dob)
    dob_entry.grid(row = 3, column = 1, padx=20, pady=(10, 0), sticky="nsew")
    mrn_entry = ct.CTkEntry(master=add_patient_info, textvariable=mrn)
    mrn_entry.grid(row = 4, column = 1, padx=20, pady=(10, 0), sticky="nsew")

    submit = ct.CTkButton(master=add_patient_info, text = "Submit", command= lambda: reorient_file(first_name.get(), last_name.get(), dob.get(), mrn.get()))
    submit.grid(row = 5, column = 1, padx=20, pady=(10, 0), sticky="w")

def reorient_file(first_name,last_name, dob, mrn):
    change_to_loading()
    print(first_name, last_name, dob, mrn)
    ext = "117"
    clinicName = "ClinicName"
    instituionName = "InstitutionName"
    gender = 'F'
    today = date.today()
    effective_time = today.strftime("%Y%m%d")
    today = today.strftime("%Y-%m-%d")
    t = time.localtime()
    current_time = time.strftime("%H%M", t)
    effective_time += current_time

    # Add info
    root = ET.Element('FamilyHistory', classCode="OBS", moodCode="EVN")
    ET.SubElement(root, 'id', root="2.16.840.1.113883.6.117", extension=ext, assigningAuthorityName="HRA" )
    ET.SubElement(root, 'code', code="10157-6",codeSystemName="LOINC", displayName="HISTORY OF FAMILY MEMBER DISEASE")
    ET.SubElement(root, 'text').text = clinicName + "; " + instituionName
    ET.SubElement(root, 'effectiveTime', value=effective_time)
    subject = ET.SubElement(root, 'subject', typeCode="SBJ")
    patient = ET.SubElement(subject, 'patient', classCode="PAT")
    ET.SubElement(patient, 'id', root="2.16.840.1.113883.6.117", extension=mrn)
    patientPerson = ET.SubElement(patient, 'patientPerson', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(patientPerson, 'id', extension="1")
    name = ET.SubElement(patientPerson, 'name')
    ET.SubElement(name, 'given').text = first_name
    ET.SubElement(name, 'family').text = last_name
    ET.SubElement(patientPerson,'administrativeGenderCode', code=gender)
    ET.SubElement(patientPerson, 'birthTime', value=dob)



    # Make file
    if(last_name != ""):
        filename = str(last_name) + ", " + str(first_name) + " " + mrn + " HL7 " + today + "-" + current_time + ".xml"
    else:
        filename = str(first_name) + " " + mrn + " HL7 " + today + "-" + current_time + ".xml"

    tree = ET.ElementTree(root)
    tree.write(filename)

def change_to_upload():
    upload.grid(row=0, column=0, sticky="nsew")
    button = ct.CTkButton(master=upload, text="Upload File", command=upload_file)
    button.grid(row=0, column=0, padx=20, pady=100)
    choose_patient.grid_forget()
    add_patient_info.grid_forget()
    download.grid_forget()
    loading.grid_forget()

def change_to_choose_patient():
    choose_patient.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    add_patient_info.grid_forget()
    upload.grid_forget()
    download.grid_forget()
    loading.grid_forget()

def change_to_add_patient():
    add_patient_info.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    choose_patient.grid_forget()
    upload.grid_forget()
    download.grid_forget()
    loading.grid_forget()

def change_to_loading():
    loading.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    add_patient_info.grid_forget()
    choose_patient.grid_forget()
    upload.grid_forget()
    download.grid_forget()

def change_to_download():
    download.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    add_patient_info.grid_forget()
    choose_patient.grid_forget()
    upload.grid_forget()
    loading.grid_forget()


relatives = []
app = create_app()
upload = Frame(app)
choose_patient = Frame(app)
add_patient_info = Frame(app)
loading = Frame(app)
download = Frame(app)
change_to_upload()
app.mainloop()
