from lxml import etree as ET
import customtkinter as ct
from tkinter import filedialog, font
from datetime import *
import time
import os

import globalVars
import rearrange_mother
import rearrange_father
import rearrange_brother
import rearrange_sister
import rearrange_son
import rearrange_daughter
import rearrange_maunt
import rearrange_paunt
import rearrange_muncle
import rearrange_puncle
import rearrange_mgrnmother
import rearrange_pgrnmother
import rearrange_pgrnfather
import rearrange_mgrnfather
import rearrange_grandchild
import rearrange_mcousin
import rearrange_pcousin
import rearrange_niece
import rearrange_nephew

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
        ct.set_appearance_mode("auto") 
        app.title("HL7 Reorientation Program")
        app.geometry("800x600")
        app.grid_rowconfigure(0, weight=1)
        app.grid_columnconfigure(0, weight=1)
        app.resizable(False, False)
        label1 = ct.CTkLabel(master=app, text="Lead Developer: Alena Durel, Charleston Southern University Student (Spring 2024 Grad)")
        label1.place(x=10, y=550)
        label2 = ct.CTkLabel(master=app, text="Assistant Developer: Riley Osborne, Charleston Southern University Student (Fall 2024 Grad)")
        label2.place(x=10, y=570)
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
    elif code == "GRNDDAU":
        return "Granddaughter -- "
    elif code == "GRNDSON":
        return "Grandson -- "
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
    elif code == "NIECE":
        return "Niece -- "
    elif code == "NEPHEW":
        return "Nephew --"
    elif code == "PCOUSN":
        return "Paternal Cousin -- "
    elif code == "MCOUSN":
        return "Maternal Cousin -- "
    elif code == "COUSN":
        return "Cousin -- "
    elif code == "NotAvailable":
        return "Unknown Relationship -- "
    elif code == "MGGRFTH":
        return "Maternal Great-Grandfather -- "
    elif code == "PGGRFTH":
        return "Paternal Great-Grandfather -- "    
    elif code == "MGGRMTH":
        return "Maternal Great-Grandmother -- "
    elif code == "PGGRMTH":
        return "Paternal Great-Grandmother -- "
    
    return (str(code) + " -- ")

def checkAvailable(code):
    if code == "NMTH":
        return True
    elif code == "NFTH":
        return True
    elif code == "MGRMTH":
        return True
    elif code == "MGRFTH":
        return True
    elif code == "PGRMTH":
        return True
    elif code == "PGRFTH":
        return True
    elif code == "DAU":
        return True
    elif code == "SON":
        return True
    elif code == "GRNDDAU":
        return True
    elif code == "GRNDSON":
        return True
    elif code == "NSIS":
        return True
    elif code == "NBRO":
        return True
    elif code == "MAUNT":
        return True
    elif code == "PAUNT":
        return True
    elif code == "MUNCLE":
        return True
    elif code == "PUNCLE":
        return True
    elif code == "NIECE":
        return True
    elif code == "NEPHEW":
        return True
    elif code == "PCOUSN":
        return True
    elif code == "MCOUSN":
        return True
    
    return False


    
def validateName(name):
    temp = ""
    if str(name) != "None":
        temp += str(name)
    return temp
    
def upload_file():
    numOfMoth = 0
    numOfFath = 0
    file= filedialog.askopenfilename(initialdir=os.getcwd(), title="Select the original patient's file", filetypes=([("XML Files","*.xml")]))
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
        raceCode = patientPerson.find('raceCode')
        if(raceCode is not None):
            globalVars.originalRace = raceCode
        ethnicCode = patientPerson.find('ethnicGroupCode')
        if(ethnicCode is not None):
            globalVars.originalEthnicity = ethnicCode

        for subjectOf1Data in patient.findall("subjectOf1"):
            globalVars.subjectOf1.append(subjectOf1Data)
        
        for subjectOf2Data in patient.findall("subjectOf2"):
            globalVars.subjectOf2.append(subjectOf2Data)

        # Get relative data
        for relative in tree.findall('.//relative'):
            code = relative.find('code')
            codeText = code.get('code')
            if(str(codeText) == "NotAvailable"):
                globalVars.relativesArray.append(relative)
                relationshipHolder = relative.find('relationshipHolder')
                name = relationshipHolder.find('name')
                currentID = str(relationshipHolder.find('id').get('extension'))
                if((int)(currentID) >= (int)(globalVars.currentMaxID)):
                    globalVars.currentMaxID = currentID
                    
                if(name is not None):
                    given = name.find('given').text
                    family = name.find('family').text
                else:
                    given = ""
                    family = ""

                relativeData = ""
                relativeData += switchCode(codeText)
                relativeData += validateName(given) + " " + validateName(family)
                globalVars.unavailableRelatives.append(relativeData)
                continue
            if(str(codeText) != "NMTH"):
                numOfMoth += 1
            if( str(codeText) != "NFTH"):
                numOfFath += 1
            relationshipHolder = relative.find('relationshipHolder')
            subjectOf1 = relative.find('subjectOf1')
            name = relationshipHolder.find('name')
            if(name is not None):
                globalVars.relativesArray.append(relative)
                given = name.find('given').text
                family = name.find('family').text
                relativeData = ""
                relativeData += switchCode(codeText)
                relativeData += validateName(given) + " " + validateName(family)
                
                if(checkAvailable(codeText) == True):
                    globalVars.relatives.append(relativeData)
                else:
                    globalVars.unavailableRelatives.append(relativeData)
                    continue

                globalVars.codes.append(codeText)
                globalVars.first_names.append(validateName(given))
                globalVars.last_names.append(validateName(family))
                currentID = str(relationshipHolder.find('id').get('extension'))
                globalVars.ids.append(currentID)
                if((int)(currentID) >= (int)(globalVars.currentMaxID)):
                    globalVars.currentMaxID = currentID
                if(codeText[0] == "M"):
                    globalVars.maternalSideIDS.append(currentID)
                elif(codeText[0] == "P"):
                    globalVars.paternalSideIDS.append(currentID)
                elif(codeText == "NSIS" or codeText == "NBRO" or codeText == "DAU" or codeText == "SON" or codeText == "GRNDDAU" or codeText == "GRNDSON"):
                    globalVars.maternalSideIDS.append(currentID)
                    globalVars.paternalSideIDS.append(currentID)
                globalVars.genders.append(relationshipHolder.find('administrativeGenderCode').get('code'))
                isDeceased = relationshipHolder.find('deceasedInd').get('value')
                globalVars.deceased.append(isDeceased)

                raceCode = relationshipHolder.find('raceCode')
                globalVars.race.append(raceCode)
                ethnicCode = relationshipHolder.find('ethnicGroupCode')
                globalVars.ethnicity.append(ethnicCode)
    
            elif((numOfMoth != 0 and str(codeText) != "NMTH") and (numOfFath != 0 and str(codeText) != "NFTH")):
                globalVars.relativesArray.append(relative)
                relativeData = ""
                relativeData += switchCode(codeText)
                if(checkAvailable(codeText) == True):
                    globalVars.relatives.append(relativeData)
                else:
                    globalVars.unavailableRelatives.append(relativeData)
                    continue

                globalVars.codes.append(codeText)
                globalVars.first_names.append("")
                globalVars.last_names.append("")
                currentID = str(relationshipHolder.find('id').get('extension'))
                globalVars.ids.append(currentID)
                if((int)(currentID) >= (int)(globalVars.currentMaxID)):
                    globalVars.currentMaxID = currentID
                if(codeText[0] == "M"):
                    globalVars.maternalSideIDS.append(currentID)
                elif(codeText[0] == "P"):
                    globalVars.paternalSideIDS.append(currentID)
                    globalVars.paternalSideIDS.append(relationshipHolder.find('id').get('extenstion'))
                globalVars.genders.append(relationshipHolder.find('administrativeGenderCode').get('code'))
                isDeceased = relationshipHolder.find('deceasedInd').get('value')
                globalVars.deceased.append(isDeceased)
                raceCode = relationshipHolder.find('raceCode')
                globalVars.race.append(raceCode)
                ethnicCode = relationshipHolder.find('ethnicGroupCode')
                globalVars.ethnicity.append(ethnicCode)

            if(subjectOf1 is not None):
                if(isDeceased == "false"):
                    globalVars.ages.append(subjectOf1.find('livingEstimatedAge').find('value').get('value'))
                else:
                    globalVars.ages.append(subjectOf1.find('deceasedEstimatedAge').find('value').get('value'))

        output_family(tree)
            

def output_family(tree):
    change_to_choose_patient()
    label1 = ct.CTkLabel(master=choose_patient, text="Additional Relatives with Insufficient Data for Reorientation:")
    label2 = ct.CTkLabel(master=choose_patient, text="------------------------------------------------------------------------------------")
        
    instructions1 = ct.CTkLabel(master=choose_patient, text="Select one of the relatives below as the new patient", font=(default_font, 20))
    instructions1.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="ew")
    instructions2 = ct.CTkLabel(master=choose_patient, text="and click the 'Choose Patient' button", font=(default_font, 20))
    instructions2.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")

    radio_var = ct.IntVar(value=2)
    i = 2
    for relativeData in globalVars.relatives:
        radioButton = ct.CTkRadioButton(master=choose_patient, text=relativeData, variable=radio_var, value = i)
        radioButton.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="ew")
        i += 1

    button = ct.CTkButton(master=choose_patient, text="Choose Patient", command= lambda: add_data(radio_var.get(), tree))
    button.grid(row=i, column=0, padx=20, pady=20)
    i += 1

    label1.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="w")
    i += 1    
    
    label2.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="w")
    i += 1

    for relativeData in globalVars.unavailableRelatives:
        label = ct.CTkLabel(master=choose_patient, text=relativeData)
        label.grid(row=i, column=0, padx=20, pady=(10, 0), sticky="w")
        i += 1

def add_data(idx, tree):
    idx = idx - 2
    change_to_add_patient()

    instructions1 = ct.CTkLabel(master=add_patient_info, text="Fill in the required data for the new patient below", font=(default_font, 20))
    instructions1.grid(row=0, column = 1, padx=20, pady=(10, 0), sticky="w")
    instructions2 = ct.CTkLabel(master=add_patient_info, text="and click the 'Submit' button", font=(default_font, 20))
    instructions2.grid(row=1, column = 1, padx=20, pady=(10, 0), sticky="w")

    first_name = ct.StringVar()
    last_name = ct.StringVar()
    dob = ct.StringVar()
    mrn = ct.StringVar()
    new_patient_label = ct.CTkLabel(master=add_patient_info, text = "New patient: " + globalVars.relatives[idx])
    new_patient_label.grid(row=2, column=1, padx=20, pady=(10, 0), sticky="w")
    first_name_label = ct.CTkLabel(master=add_patient_info, text = "First Name")
    first_name_label.grid(row = 3, column = 0, padx=20, pady=(10, 0), sticky="w")
    last_name_label = ct.CTkLabel(master=add_patient_info, text = "Last Name")
    last_name_label.grid(row = 4, column = 0, padx=20, pady=(10, 0), sticky="w")
    dob_label = ct.CTkLabel(master=add_patient_info, text = "Date of Birth (YYYYMMDD)")
    dob_label.grid(row = 5, column = 0, padx=20, pady=(10, 0), sticky="w")
    mrn_label =  ct.CTkLabel(master=add_patient_info, text = "Medical Record Number")
    mrn_label.grid(row = 6, column = 0, padx=20, pady=(10, 0), sticky="w")
    first_name_entry = ct.CTkEntry(master=add_patient_info, textvariable=first_name)
    first_name_entry.insert(0, globalVars.first_names[idx])
    first_name_entry.grid(row = 3, column = 1, padx=20, pady=(10, 0), sticky="nsew")
    last_name_entry = ct.CTkEntry(master=add_patient_info, textvariable=last_name)
    last_name_entry.insert(0, globalVars.last_names[idx])
    last_name_entry.grid(row = 4, column = 1, padx=20, pady=(10, 0), sticky="nsew")
    dob_entry = ct.CTkEntry(master=add_patient_info, textvariable=dob)
    dob_entry.grid(row = 5, column = 1, padx=20, pady=(10, 0), sticky="nsew")
    mrn_entry = ct.CTkEntry(master=add_patient_info, textvariable=mrn)
    mrn_entry.grid(row = 6, column = 1, padx=20, pady=(10, 0), sticky="nsew")


    submit = ct.CTkButton(master=add_patient_info, text = "Submit", command= lambda: validate(first_name.get(), last_name.get(), dob.get(), mrn.get(), idx, tree))
    submit.grid(row = 7, column = 1, padx=20, pady=(10, 0), sticky="w")

def validate(first_name, last_name, dob, mrn, idx, tree):
    if(first_name != "" and last_name != "" and dob != "" and mrn != ""):
        reorient_file(first_name, last_name,dob, mrn, idx, tree)
    else:
        change_to_invalid()

def reorient_file(first_name,last_name, dob, mrn, idx, tree):
    change_to_loading()
    # print(first_name, last_name, dob, mrn)
    ext = str(int(tree.find('.id').get("extension")) + 1)
    clinicName = tree.find(".//text").text
    ExistingRoot = str(tree.find('.id').get("root"))
    today = date.today()
    effective_time = today.strftime("%Y%m%d")
    today = today.strftime("%Y-%m-%d")
    t = time.localtime()
    current_time = time.strftime("%H%M", t)
    effective_time += current_time

    # Add info
    root = ET.Element('FamilyHistory', classCode="OBS", moodCode="EVN")
    ET.SubElement(root, 'id', root= ExistingRoot, extension=ext, assigningAuthorityName="HRA" )
    ET.SubElement(root, 'code', code="10157-6",codeSystemName="LOINC", displayName="HISTORY OF FAMILY MEMBER DISEASE")
    ET.SubElement(root, 'text').text = clinicName
    ET.SubElement(root, 'effectiveTime', value=effective_time)
    subject = ET.SubElement(root, 'subject', typeCode="SBJ")
    patient = ET.SubElement(subject, 'patient', classCode="PAT")
    ET.SubElement(patient, 'id', root=ExistingRoot, extension=mrn)
    patientPerson = ET.SubElement(patient, 'patientPerson', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(patientPerson, 'id', extension="1")
    name = ET.SubElement(patientPerson, 'name')
    ET.SubElement(name, 'given').text = first_name
    ET.SubElement(name, 'family').text = last_name
    ET.SubElement(patientPerson,'administrativeGenderCode', code=globalVars.genders[idx])
    ET.SubElement(patientPerson, 'birthTime', value=dob)
    ET.SubElement(patientPerson, 'deceasedInd', value=globalVars.deceased[idx])
    if(globalVars.race[idx] is not None):
        patientPerson.append(globalVars.race[idx])
    if(globalVars.ethnicity[idx] is not None):
        patientPerson.append(globalVars.ethnicity[idx])

    # Break out for rearranging

    #Modify Relatives
    ## Global variable array is for accessint the id of the relative before they became the patient

    #if new patient is
    
    # brother
    if(str(globalVars.codes[idx]) == "NBRO"):
        rearrange_brother.rearrange(tree, patientPerson, globalVars.ids[idx])
    # sister
    if(str(globalVars.codes[idx]) == "NSIS"):
        rearrange_sister.rearrange(tree, patientPerson, globalVars.ids[idx])
    # mother
    if(str(globalVars.codes[idx]) == "NMTH"):
        rearrange_mother.rearrange(tree, patientPerson)
    # father
    if(str(globalVars.codes[idx]) == "NFTH"):
        rearrange_father.rearrange(tree, patientPerson)
    # son
    if(str(globalVars.codes[idx]) == "SON"):
        rearrange_son.rearrange(tree, patientPerson, globalVars.ids[idx])
    # daughter
    if(str(globalVars.codes[idx]) == "DAU"):
        rearrange_daughter.rearrange(tree, patientPerson, globalVars.ids[idx])
    # grandparent
    if(str(globalVars.codes[idx])== "MGRMTH"):
       rearrange_mgrnmother.rearrange(tree, patientPerson)
    if(str(globalVars.codes[idx])== "PGRMTH"):
       rearrange_pgrnmother.rearrange(tree, patientPerson)
    if(str(globalVars.codes[idx])== "MGRFTH"):
       rearrange_mgrnfather.rearrange(tree, patientPerson)
    if(str(globalVars.codes[idx])== "PGRFTH"):
       rearrange_pgrnfather.rearrange(tree, patientPerson)
    # grandchild
    if(str(globalVars.codes[idx]) == "GRNDDAU" or str(globalVars.codes[idx]) == "GRNDSON"):
        rearrange_grandchild.rearrange(tree, patientPerson, globalVars.ids[idx])
    # aunt
    if(str(globalVars.codes[idx]) == "MAUNT"):
        rearrange_maunt.rearrange(tree, patientPerson, globalVars.ids[idx])
    if(str(globalVars.codes[idx]) == "PAUNT"):
        rearrange_paunt.rearrange(tree, patientPerson, globalVars.ids[idx])
    # uncle    
    if(str(globalVars.codes[idx]) == "MUNCLE"):
        rearrange_muncle.rearrange(tree, patientPerson, globalVars.ids[idx])
    if(str(globalVars.codes[idx]) == "PUNCLE"):
        rearrange_puncle.rearrange(tree, patientPerson, globalVars.ids[idx])
    # cousin
    if(str(globalVars.codes[idx]) == "MCOUSN"):
        rearrange_mcousin.rearrange(tree, patientPerson, globalVars.ids[idx])
    if(str(globalVars.codes[idx]) == "PCOUSN"):
        rearrange_pcousin.rearrange(tree, patientPerson, globalVars.ids[idx])
    # niece
    if(str(globalVars.codes[idx]) == "NIECE"):
        rearrange_niece.rearrange(tree, patientPerson, globalVars.ids[idx])
    # nephew
    if(str(globalVars.codes[idx]) == "NEPHEW"):
        rearrange_nephew.rearrange(tree, patientPerson, globalVars.ids[idx])

    for data in globalVars.newPatientSubjectOf1:
        patient.append(data)

    for data in globalVars.newPatientSubjectOf2:
        patient.append(data)



    # Make file
    if(last_name != ""):
        filename = str(last_name) + ", " + str(first_name) + " " + mrn + " HL7 " + today + "-" + current_time + ".xml"
    else:
        filename = str(first_name) + " " + mrn + " HL7 " + today + "-" + current_time + ".xml"

    name = str(last_name) + ", " + str(first_name)
    
    change_to_download(root, filename, name)

   

def download_file(root, filename):
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)
    directory=filedialog.askdirectory(initialdir=os.getcwd(), title="Select a directory to download {} to".format(filename))
    if(directory):
        tree.write(directory + "/" + filename, xml_declaration=True, encoding='UTF-8')
        change_to_success()

def change_to_upload():
    upload.grid(row=0, column=0, pady=(0, 50), sticky="nsew")
    label = ct.CTkLabel(master=upload, text="Click the 'Upload File' button to select the original patient's HL7 File", font=(default_font, 20))
    label.grid(row=0, column=0, padx=20, pady=20)
    button = ct.CTkButton(master=upload, text="Upload File", command=upload_file)
    button.grid(row=1, column=0, padx=20, pady=100)
    choose_patient.grid_forget()
    add_patient_info.grid_forget()
    download.grid_forget()
    loading.grid_forget()
    success.grid_forget()

def change_to_choose_patient():
    choose_patient.grid(row=0, column=0, padx=10, pady=(0, 50), sticky="nsew")
    add_patient_info.grid_forget()
    upload.grid_forget()
    download.grid_forget()
    loading.grid_forget()
    success.grid_forget()

def change_to_add_patient():
    add_patient_info.grid(row=0, column=0, pady= (0, 50) , sticky="nsew")
    choose_patient.grid_forget()
    upload.grid_forget()
    download.grid_forget()
    loading.grid_forget()
    success.grid_forget()

def change_to_loading():
    loading.grid(row=0, column=0, pady=(0, 50), sticky="nsew")
    add_patient_info.grid_forget()
    choose_patient.grid_forget()
    upload.grid_forget()
    download.grid_forget()
    success.grid_forget()

def change_to_success():
    success.grid(row=0, column=0, pady=(0, 50), sticky="nsew")
    label = ct.CTkLabel(master=success, text = "Download Successful", font=(default_font, 20))
    label.grid(row = 0, column = 0, padx=20, pady=10)
    button = ct.CTkButton(master=success, text="Back", command=back)
    button.grid(row=1, column=0, padx=20, pady=100)
    loading.grid_forget()
    add_patient_info.grid_forget()
    choose_patient.grid_forget()
    upload.grid_forget()

def back():
    success.grid_forget()

def change_to_invalid():
    success.grid(row=0, column=0, pady=(0, 50), sticky="nsew")
    label = ct.CTkLabel(master=success, text = "Invalid Data", font=(default_font, 20))
    label.grid(row = 0, column = 0, padx=20, pady=10)
    button = ct.CTkButton(master=success, text="Back", command=back)
    button.grid(row=1, column=0, padx=20, pady=100)
    loading.grid_forget()
    choose_patient.grid_forget()
    upload.grid_forget()
    download.grid_forget()

def back_to_add():
    invalid.grid_forget()

def reset():
    globalVars.reset()
    for widgets in choose_patient.winfo_children():
      widgets.destroy()
    change_to_upload()

def change_to_download(tree, filename, name):
    download.grid(row=0, column=0, pady=(0, 50), sticky="nsew")

    label = ct.CTkLabel(master=download, text="HL7 File Generated for " + name, font=(default_font, 30))
    label.grid(row=0, column=0, padx=20, pady=5)
    instructions1 = ct.CTkLabel(master=download, text="Click the 'Download File' button to download the HL7", font=(default_font, 20))
    instructions1.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")
    instructions2 = ct.CTkLabel(master=download, text="file generated for the new patient", font=(default_font, 20))
    instructions2.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="ew")

    button = ct.CTkButton(master=download, text="Download File", command= lambda: download_file(tree, filename))
    button.grid(row=3, column=0, padx=20, pady=50)

    instructions3 = ct.CTkLabel(master=download, text="Click the 'Restart' button to restart the program", font=(default_font, 15))
    instructions3.grid(row=4, column=0, padx=20, pady=(20, 0), sticky="ew")
    button = ct.CTkButton(master=download, text="Restart", command=reset)
    button.grid(row=5, column=0, padx=20, pady=10)
    
    instructions4 = ct.CTkLabel(master=download, text="Click the 'Quit' button to exit", font=(default_font, 15))
    instructions4.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="ew")

    button = ct.CTkButton(master=download, text="Quit", command=app.destroy)
    button.grid(row = 7, column=0, padx=20, pady=10)
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
success = Frame(app)
invalid = Frame(app)
default_font = font.nametofont("TkTextFont")
default_font.actual()
change_to_upload()
app.mainloop()
