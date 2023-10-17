import xml.etree.ElementTree as ET
import customtkinter as ct
from tkinter import filedialog
from datetime import *
import time

import globalVars
import rearrange_mother
import rearrange_father
import rearrange_sibling
import rearrange_child


class Frame(ct.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

class ScrollableFrame(ct.CTkScrollableFrame):
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
    elif code == "SON":
        return "Son -- "
    elif code == "NSIS":
        return "Sister -- "
    elif code == "NBRO":
        return "Brother -- " 
    elif code == "MAUNT":
        return "Maternal Aunt -- "
    elif code == "PAUNT":
        return "Paternal Aunt -- "
    elif code == "MUNCLE":
        return "Maternal Uncle -- "
    elif code == "PUNCLE":
        return "Paternal Uncle -- "

    return str(code)
    
def validateName(name):
    temp = ""
    if str(name) != "None":
        temp += str(name)
    return temp
    
def upload_file():
    numOfMoth = 0
    numOfFath = 0
    file= filedialog.askopenfilename(title="Select the original patient's file", filetypes=([("XML Files","*.xml")]))
    if file:
        tree = ET.parse(file)
        # Get patient data
        subject = tree.find('subject')
        patient = subject.find('.//patient')
        patientPerson = patient.find('patientPerson')
        name = patientPerson.find('name')
        given = name.find('given').text
        family = name.find('family').text
        globalVars.originalGivenName = validateName(given)
        globalVars.originalFamilyName = validateName(family)
        globalVars.originalGender = patientPerson.find('administrativeGenderCode').get('code')
        globalVars.originalDOB = patientPerson.find('birthTime').get('value')
        globalVars.originalDeceased = patientPerson.find('deceasedInd').get('value')

        for subjectOf1Data in patient.findall("subjectOf1"):
            globalVars.subjectOf1.append(subjectOf1Data)
        
        for subjectOf2Data in patient.findall("subjectOf2"):
            globalVars.subjectOf2.append(subjectOf2Data)

        # Get relative data
        for relative in tree.findall('.//relative'):
            code = relative.find('code')
            codeText = code.get('code')
            if(str(codeText) == "NotAvailable"):
                continue
            if(str(codeText) != "NMTH"):
                numOfMoth += 1
            if( str(codeText) != "NFTH"):
                numOfFath += 1
            relationshipHolder = relative.find('relationshipHolder')
            subjectOf1 = relative.find('subjectOf1')
            name = relationshipHolder.find('name')
            if(name):
                globalVars.relativesArray.append(relative)
                given = name.find('given').text
                family = name.find('family').text
                relativeData = ""
                relativeData += switchCode(codeText)
                relativeData += validateName(given) + " " + validateName(family)
                globalVars.relatives.append(relativeData)

                globalVars.codes.append(codeText)
                globalVars.first_names.append(validateName(given))
                globalVars.last_names.append(validateName(family))
                globalVars.ids.append(relationshipHolder.find('id').get('extenstion'))
                globalVars.genders.append(relationshipHolder.find('administrativeGenderCode').get('code'))
                isDeceased = relationshipHolder.find('deceasedInd').get('value')
                globalVars.deceased.append(isDeceased)
            elif((numOfMoth != 0 and str(codeText) != "NMTH") and (numOfFath != 0 and str(codeText) != "NFTH")):
                globalVars.relativesArray.append(relative)
                relativeData = ""
                relativeData += switchCode(codeText)
                globalVars.relatives.append(relativeData)

                globalVars.codes.append(codeText)
                globalVars.first_names.append("")
                globalVars.last_names.append("")
                globalVars.ids.append(relationshipHolder.find('id').get('extenstion'))
                globalVars.genders.append(relationshipHolder.find('administrativeGenderCode').get('code'))
                isDeceased = relationshipHolder.find('deceasedInd').get('value')
                globalVars.deceased.append(isDeceased)

            if(subjectOf1):
                if(isDeceased == "false"):
                    globalVars.ages.append(subjectOf1.find('livingEstimatedAge').find('value').get('value'))
                else:
                    globalVars.ages.append(subjectOf1.find('deceasedEstimatedAge').find('value').get('value'))

        output_family(tree)
            

def output_family(tree):
    change_to_choose_patient()
    radio_var = ct.IntVar(value=0)
    i = 0
    for relativeData in globalVars.relatives:
        radioButton = ct.CTkRadioButton(master=choose_patient, text=relativeData, variable=radio_var, value = i)
        radioButton.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="ew")
        i += 1

    button = ct.CTkButton(master=choose_patient, text="Choose Patient", command= lambda: add_data(radio_var.get(), tree))
    button.grid(row=i, column=0, padx=20, pady=20)

def add_data(idx, tree):
    change_to_add_patient()
    first_name = ct.StringVar()
    last_name = ct.StringVar()
    dob = ct.StringVar()
    mrn = ct.StringVar()
    new_patient_label = ct.CTkLabel(master=add_patient_info, text = "New patient: " + globalVars.relatives[idx])
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

    submit = ct.CTkButton(master=add_patient_info, text = "Submit", command= lambda: reorient_file(first_name.get(), last_name.get(), dob.get(), mrn.get(), idx, tree))
    submit.grid(row = 5, column = 1, padx=20, pady=(10, 0), sticky="w")


def reorient_file(first_name,last_name, dob, mrn, idx, tree):
    change_to_loading()
    print(first_name, last_name, dob, mrn)
    ext = "117"
    clinicName = tree.find(".//text").text
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
    ET.SubElement(root, 'text').text = clinicName
    ET.SubElement(root, 'effectiveTime', value=effective_time)
    subject = ET.SubElement(root, 'subject', typeCode="SBJ")
    patient = ET.SubElement(subject, 'patient', classCode="PAT")
    ET.SubElement(patient, 'id', root="2.16.840.1.113883.6.117", extension=mrn)
    patientPerson = ET.SubElement(patient, 'patientPerson', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(patientPerson, 'id', extension="1")
    name = ET.SubElement(patientPerson, 'name')
    ET.SubElement(name, 'given').text = first_name
    ET.SubElement(name, 'family').text = last_name
    ET.SubElement(patientPerson,'administrativeGenderCode', code=globalVars.genders[idx])
    ET.SubElement(patientPerson, 'birthTime', value=dob)
    ET.SubElement(patientPerson, 'deceasedInd', value=globalVars.deceased[idx])

    # Break out for rearranging

    #Modify Relatives

    #if new patient is

    # sibling
    if(str(globalVars.codes[idx]) == "NSIS" or str(globalVars.codes[idx]) == "NBRO"):
        rearrange_sibling.rearrange(tree, patientPerson)
    # mother
    if(str(globalVars.codes[idx]) == "NMTH"):
        rearrange_mother.rearrange(tree, patientPerson)
    # father
    if(str(globalVars.codes[idx]) == "NFTH"):
        rearrange_father.rearrange(tree, patientPerson)
    # child
    if(str(globalVars.codes[idx]) == "DAU" or str(globalVars.codes[idx]) == "SON"):
        rearrange_child.rearrange(tree, patientPerson)
    # grandparent

    # TODO: Add any subjectOf1 and subjectOf2 data for new patient


    # # Modify extension
    # extension = tree.find(".//id").get('extension')
    # tree.find(".//id").set('extension', (str(int(extension) + 1)))
    # # Modify effective time
    # tree.find(".//effectiveTime").set('value', effective_time)
    # # Modify the MRN
    # patient = tree.find(".//patient")
    # patient.find(".//id").set('extension', mrn)
    # # Modify patient info
    # patientPerson = tree.find(".//patientPerson")
    # name = patientPerson.find('name')
    # given = name.find('given')
    # given.text = first_name
    # family = name.find('family')
    # family.text = last_name

    # patientPerson.find('administrativeGenderCode').set('code', genders[idx])
    # patientPerson.find('birthTime').set('value', dob)
    # patientPerson.find('deceasedInd').set('value', deceased[idx])

    # subjectOf1Info = patient.find('subjectOf1')
    # if(deceased[idx] == 'false'):
    #     subjectOf1Info.find('livingEstimatedAge').find('value').set('value', ages[idx])
    #     subjectOf1Info.find('livingEstimatedAge').find('code').set('code', "21611-9")

    # else:
    #     subjectOf1Info.find('deceasedEstimatedAge').find('value').set('value', ages[idx])
    #     subjectOf1Info.find('deceasedEstimatedAge').find('code').set('code', "39016-1")


    #hi

    # Make file
    if(last_name != ""):
        filename = str(last_name) + ", " + str(first_name) + " " + mrn + " HL7 " + today + "-" + current_time + ".xml"
    else:
        filename = str(first_name) + " " + mrn + " HL7 " + today + "-" + current_time + ".xml"

    
    change_to_download(root, filename)

   

def download_file(root, filename):
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    directory=filedialog.askdirectory(initialdir="/home/", title="Select a directory to download {}".format(filename))
    if(directory):
        tree.write(directory + "/" + filename, encoding="utf-8")

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

def change_to_download(tree, filename):
    download.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    button = ct.CTkButton(master=download, text="Download File", command= lambda: download_file(tree, filename))
    button.grid(row=0, column=0, padx=20, pady=100)

    button = ct.CTkButton(master=download, text="Quit", command=quit)
    button.grid(row=1, column=0, padx=20, pady=100)
    add_patient_info.grid_forget()
    choose_patient.grid_forget()
    upload.grid_forget()
    loading.grid_forget()


app = create_app()
upload = Frame(app)
choose_patient = ScrollableFrame(app)
add_patient_info = Frame(app)
loading = Frame(app)
download = Frame(app)
change_to_upload()
app.mainloop()
