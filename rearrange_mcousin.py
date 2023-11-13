import globalVars
from lxml import etree as ET

def determineFamilySide(newPatientOldID):
    global newPatientMotherID
    global newPatientFatherID
    familyside = ""
    for relative in globalVars.relativesArray:
        if((str)(relative.find('code').get('code'))== "MCOUSN"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            if((str)(id) == (str)(newPatientOldID)):
                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        motherID = relationshipHolderNew.find('id').get('extension')
                        newPatientMotherID = motherID
                        if(motherID in globalVars.maternalSideIDS):
                            familyside = "M"
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        fatherID = relationshipHolderNew.find('id').get('extension')
                        newPatientFatherID = fatherID
                        if(fatherID in globalVars.maternalSideIDS):
                            familyside = "P"

    return familyside

# Create a new relative element to hold the original patient's information.
# Since this function correlates to the rearrange_granddau section, the original
# patient will become a cousin
def makeRelativeForOldPatient(originalPatient, fatherId, motherId, currentId, sideOfFamily):
    ET.SubElement(originalPatient, 'code', code = ((str)(sideOfFamily)) + "COUSN")
    patientRelationshipHolder = ET.SubElement(originalPatient, 'relationshipHolder', classCode = "PSN", determinerCode="INSTANCE")
    ET.SubElement(patientRelationshipHolder, 'id', extension = str(currentId))
    originalPatientID = currentId
    name = ET.SubElement(patientRelationshipHolder, 'name')
    ET.SubElement(name, 'given').text = globalVars.originalGivenName
    ET.SubElement(name, 'family').text = globalVars.originalFamilyName
    ET.SubElement(patientRelationshipHolder, 'administrativeGenderCode', code = globalVars.originalGender)
    ET.SubElement(patientRelationshipHolder, 'birthTime', code = globalVars.originalDOB)
    ET.SubElement(patientRelationshipHolder, 'deceasedInd', value = globalVars.originalDeceased)
    if(globalVars.originalRace is not None):
        patientRelationshipHolder.append(globalVars.originalRace)
    if(globalVars.originalEthnicity is not None):
        patientRelationshipHolder.append(globalVars.originalEthnicity)
    
    NMTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    ET.SubElement(NMTHRelative, 'code', code = "NMTH")
    relationshipHolderNew = ET.SubElement(NMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderNew, 'id', extension=str(motherId))     # Update the original patient's mother id to reflect his new id
    NFTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    ET.SubElement(NFTHRelative, 'code', code = "NFTH")
    relationshipHolderNew = ET.SubElement(NFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderNew, 'id', extension=str(fatherId)) # Update the original patient's father id to reflect his new id

    # Add 'subjectOf1' info (estimatedAge)
    for data in globalVars.subjectOf1:
        originalPatient.append(data)

    # Add 'subjectOf2' info (clinical observation)
    for data in globalVars.subjectOf2:
        originalPatient.append(data)

    return originalPatientID

# The main function to rearrange and generate the new HL7 file.
# The first 7 IDs will be fixed and only relatives holding these IDs or linked to these IDs
# will have updates made to their IDs
# These are:
    # 1 - Patient
    # 2 - Mother
    # 3 - Father
    # 4 - Maternal Grandmother
    # 5 - Maternal Grandfather
    # 6 - Paternal Grandmother
    # 7 - Paternal Grandfather
def rearrange(tree, patientPerson, newPatientOldID):
    global oldPatientSpouse
    global newPatientFatherID
    global newPatientMotherID
    sideOfFamily = determineFamilySide(newPatientOldID)
    currentId = (int)(max(globalVars.ids)) + 1 # Any new relatives to be added will start with the next available ID

    # The first 6 members of the family will be dealt with first.
    # This includes the mother, father, maternal grandmother, and maternal grandfather
    for x in range(6):
        relative = globalVars.relativesArray[x]
        # print(relative.find('code').get('code'))

        # Maternal Grandmother -> either maternal or paternal grandmother
        if((str)(relative.find('code').get('code'))== "MGRMTH"):
            relative.find(".//code").set('code', (str)(sideOfFamily) + "GRMTH") 
            relationshipHolder = relative.find(".//relationshipHolder")
            if(sideOfFamily == "M"):
                relationshipHolder.find(".//id").set('extension', "4")
            else:
                relationshipHolder.find(".//id").set('extension', "6")
            ogmgrmth = relative
        # Maternal Grandfather -> either maternal or paternal grandfather
        elif((str)(relative.find('code').get('code'))== "MGRFTH"):
            relative.find(".//code").set('code', (str)(sideOfFamily  + "GRFTH")) 
            relationshipHolder = relative.find(".//relationshipHolder")
            if(sideOfFamily == "M"):
                relationshipHolder.find(".//id").set('extension', "5")
            else:
                relationshipHolder.find(".//id").set('extension', "7")
            ogmgrfth = relative
        #Father - Not available
        elif((str)(relative.find(".//code").get('code')) == "NFTH"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since we are essentially creating a new relative, we need a completely new ID
            relationshipHolder.find(".//id").set('extension', str(currentId)) 
            OGfatherID = currentId
            currentId += 1

            # Since the original father's parents are in-laws we can remove them
            for x in relationshipHolder.findall(".//relative"):
                relationshipHolder.remove(x)

            # Note that we are creating a new relative (father) that will be added to the HL7 later
            # rather than being appending now
            OGfather = relative
        elif((str)(relative.find(".//code").get('code')) == "NMTH"):
            # The original patient's mother becomes the new patient's aunt
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "AUNT"))
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since we are essentially creating a new relative, we need a completely new ID
            relationshipHolder.find(".//id").set('extension', str(currentId)) 
            OGmotherID = currentId
            currentId += 1

            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(str(sideOfFamily) == "M"):
                        relationshipHolderNew.find('id').set('extension', "4")
                    else:
                        relationshipHolderNew.find('id').set('extension', "6")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(str(sideOfFamily) == "M"):
                        relationshipHolderNew.find('id').set('extension', "5")
                    else:
                        relationshipHolderNew.find('id').set('extension', "7")

            # Note that we are creating a new relative (mother) that will be added to the HL7 later
            # rather than being appending now
            OGmother = relative

    # Create a new relative element for the original patient
    # This action is completed here to ensure that the original patient's parent's IDs has already been created
    originalPatient = ET.Element('relative', classCode = "PRS")
    originalPatientID = makeRelativeForOldPatient(originalPatient, OGfatherID, OGmotherID, currentId, sideOfFamily)
    currentId += 1

    # Create new parents (these will get updated later)
    NewMotherRelative = ET.SubElement(patientPerson, 'relative', classCode="PRS")
    ET.SubElement(NewMotherRelative, 'code', code="NMTH")
    relationshipHolderNew = ET.SubElement(NewMotherRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderNew, 'id', extension="2")
    name = ET.SubElement(relationshipHolderNew, 'name')
    ET.SubElement(name, 'given')
    ET.SubElement(name, 'family')
    ET.SubElement(relationshipHolderNew, 'administrativeGenderCode', code="F")
    ET.SubElement(relationshipHolderNew, 'deceasedInd', value = "false")
    mother = ET.SubElement(relationshipHolderNew, 'relative', classCode = "PRS")
    ET.SubElement(mother, 'code', code="NMTH")
    relationshipHolderMother = ET.SubElement(mother, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderMother, 'id', extension="4")
    father = ET.SubElement(relationshipHolderNew, 'relative', classCode = "PRS")
    ET.SubElement(father, 'code', code="NFTH")
    relationshipHolderFather = ET.SubElement(father, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderFather, 'id', extension="5")

    NewFatherRelative = ET.SubElement(patientPerson, 'relative', classCode="PRS")
    ET.SubElement(NewFatherRelative, 'code', code="NFTH")
    relationshipHolderNew = ET.SubElement(NewFatherRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderNew, 'id', extension="3")
    name = ET.SubElement(relationshipHolderNew, 'name')
    ET.SubElement(name, 'given')
    ET.SubElement(name, 'family')
    ET.SubElement(relationshipHolderNew, 'administrativeGenderCode', code="M")
    ET.SubElement(relationshipHolderNew, 'deceasedInd', value = "false")
    mother = ET.SubElement(relationshipHolderNew, 'relative', classCode = "PRS")
    ET.SubElement(mother, 'code', code="NMTH")
    relationshipHolderMother = ET.SubElement(mother, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderMother, 'id', extension="6")
    father = ET.SubElement(relationshipHolderNew, 'relative', classCode = "PRS")
    ET.SubElement(father, 'code', code="NFTH")
    relationshipHolderFather = ET.SubElement(father, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderFather, 'id', extension="7")

    # Make grandparents, either the maternal or paternal side will be replaced later
    if(sideOfFamily == "P"):

        MGRMTHRelative = ET.SubElement(patientPerson, 'relative', classCode="PRS")
        ET.SubElement(MGRMTHRelative, 'code', code="MGRMTH")
        relationshipHolderNew = ET.SubElement(MGRMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="4")
        ET.SubElement(relationshipHolderNew, 'administrativeGenderCode', code="F")
        ET.SubElement(relationshipHolderNew, 'deceasedInd', value = "false")

        MGRFTHRelative = ET.SubElement(patientPerson, 'relative', classCode="PRS")
        ET.SubElement(MGRFTHRelative, 'code', code="MGRFTH")
        relationshipHolderNew = ET.SubElement(MGRFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="5")
        ET.SubElement(relationshipHolderNew, 'administrativeGenderCode', code="M")
        ET.SubElement(relationshipHolderNew, 'deceasedInd', value = "false")

        patientPerson.append(ogmgrmth)
        patientPerson.append(ogmgrfth)
    else:
        patientPerson.append(ogmgrmth)
        patientPerson.append(ogmgrfth)

        PGRMTHRelative = ET.SubElement(patientPerson, 'relative', classCode="PRS")
        ET.SubElement(PGRMTHRelative, 'code', code="PGRMTH")
        relationshipHolderNew = ET.SubElement(PGRMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="6")
        ET.SubElement(relationshipHolderNew, 'administrativeGenderCode', code="F")
        ET.SubElement(relationshipHolderNew, 'deceasedInd', value = "false")

        PGRFTHRelative = ET.SubElement(patientPerson, 'relative', classCode="PRS")
        ET.SubElement(PGRFTHRelative, 'code', code="PGRFTH")
        relationshipHolderNew = ET.SubElement(PGRFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="7")
        ET.SubElement(relationshipHolderNew, 'administrativeGenderCode', code="M")
        ET.SubElement(relationshipHolderNew, 'deceasedInd', value = "false")
            
    # Continue to go through the rest of the relatives
    for x in range(6, len(globalVars.relativesArray)):
        relative = globalVars.relativesArray[x]
        # print(relative.find('code').get('code'))

        # Sister -> great aunt (not available)
        if((str)(relative.find('code').get('code'))== "NSIS"):
            relative.find(".//code").set('code', str(sideOfFamily) + "COUSN")
            relationshipHolder = relative.find(".//relationshipHolder")
 
            # Link mother -> new relative created for mother
            # Link father -> new relative created for father
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(OGmotherID))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(OGfatherID)) 
            patientPerson.append(relative)

        # Brother -> great uncle
        elif((str)(relative.find('code').get('code'))== "NBRO"):
            relative.find(".//code").set('code', str(sideOfFamily) + "COUSN")
            relationshipHolder = relative.find(".//relationshipHolder")

            # Link mother -> new relative created for mother
            # Link father -> new relative created for father
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension',  str(OGmotherID))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(OGfatherID))
            patientPerson.append(relative)

        # Maternal Aunt -> Mother or aunt
        elif((str)(relative.find('code').get('code'))== "MAUNT"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            if((str)(id) == (str)(newPatientMotherID)):
                relative.find(".//code").set('code', "NMTH")
                relationshipHolder.find(".//id").set('extension', "2") 

                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "4")
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "5")

                patientPerson.insert(patientPerson.index(NewMotherRelative),relative)
                patientPerson.remove(NewMotherRelative)
            else:
                relative.find(".//code").set('code', str(sideOfFamily) + "AUNT")

                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        if(str(sideOfFamily) == "M"):
                            relationshipHolderNew.find('id').set('extension', "4")
                        else:
                            relationshipHolderNew.find('id').set('extension', "6")
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        if(str(sideOfFamily) == "M"):
                            relationshipHolderNew.find('id').set('extension', "5")
                        else:
                            relationshipHolderNew.find('id').set('extension', "7")
                patientPerson.append(relative)
        # Maternal Uncle -> father or uncle
        elif((str)(relative.find('code').get('code'))== "MUNCLE"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            if((str)(id) == (str)(newPatientFatherID)):
                relative.find(".//code").set('code', "NFTH")
                relationshipHolder.find(".//id").set('extension', "3") 

                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "6")
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "7")

                patientPerson.insert(patientPerson.index(NewMotherRelative),relative)
                patientPerson.remove(NewMotherRelative)
            else:
                relative.find(".//code").set('code', str(sideOfFamily) + "UNCLE")

                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        if(str(sideOfFamily) == "M"):
                            relationshipHolderNew.find('id').set('extension', "4")
                        else:
                            relationshipHolderNew.find('id').set('extension', "6")
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        if(str(sideOfFamily) == "M"):
                            relationshipHolderNew.find('id').set('extension', "5")
                        else:
                            relationshipHolderNew.find('id').set('extension', "7")
                patientPerson.append(relative)
        # Niece -> NotAvailable
        elif((str)(relative.find('code').get('code'))== "NIECE"):
            motherID = 0
            fatherID = 0
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                    
            patientPerson.append(relative)
        # Nephew -> Not Available
        elif((str)(relative.find('code').get('code'))== "NEPHEW"):
            motherID = 0
            fatherID = 0
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(fatherID)

            patientPerson.append(relative)
        # Cousin -> Cousin, bro/sis, or patient
        elif((str)(relative.find('code').get('code'))== "MCOUSN"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            gender = relationshipHolder.find('administrativeGenderCode').get('code')
            child = False
            if(str(id) == (str)(newPatientOldID)):
                for subjectOf1Data in relative.findall('.//subjectOf1'):
                    globalVars.newPatientSubjectOf1.append(subjectOf1Data)
                for subjectOf2Data in relative.findall('.//subjectOf2'):
                    globalVars.newPatientSubjectOf1.append(subjectOf2Data)
            else:
                # In case one of their parents is "Not Available", we will add both to our 'notAvailableIdsToAdd' array
                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        motherID = relationshipHolderNew.find('id').get('extension')
                        globalVars.notAvailableIdsToAdd.append(motherID)
                        if(motherID == newPatientMotherID):
                            child = True
                            relationshipHolderNew.find('id').set('extension', "2")
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        fatherID = relationshipHolderNew.find('id').get('extension')
                        globalVars.notAvailableIdsToAdd.append(fatherID)
                        if(fatherID == newPatientFatherID):
                            child = True
                            relationshipHolderNew.find('id').set('extension', "3")

                if(child == False):
                    relative.find(".//code").set('code', (str)(sideOfFamily) + "COUSN")
                    patientPerson.append(relative)
                else:
                    if(gender == "F"):
                        relative.find(".//code").set('code', "NSIS")
                    else:
                        relative.find(".//code").set('code', "NBRO")
                    patientPerson.append(relative)

        # Daughter/Son -> Not available
        elif((str)(relative.find('code').get('code'))== "DAU" or (str)(relative.find('code').get('code'))== "SON"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')

            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    relationshipHolderNew.find('id').set('extension', str(OGmotherID))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    relationshipHolderNew.find('id').set('extension', str(OGfatherID))

            patientPerson.append(relative)
        #Granddaughter/Grandson -> NotAvailable
        elif((str)(relative.find('code').get('code'))== "GRNDDAU" or (str)(relative.find('code').get('code'))== "GRNDSON"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')
 
            # In case one of their parents is "Not Available", we will add both to our 'notAvailableIdsToAdd' array
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    globalVars.notAvailableIdsToAdd.append(fatherID)

            patientPerson.append(relative)
        # Maternal Great-Grandmother -> M or PGGRMTH
        elif((str)(relative.find('code').get('code'))== "MGGRMTH"):
            relative.find(".//code").set('code', str(sideOfFamily) + "GGRMTH")
            relationshipHolder = relative.find(".//relationshipHolder")

            patientPerson.append(relative)
        # Maternal Great-Grandfather -> M or PGGRFTH
        elif((str)(relative.find('code').get('code'))== "MGGRFTH"):
            relative.find(".//code").set('code', str(sideOfFamily) + "GGRFTH")
            relationshipHolder = relative.find(".//relationshipHolder")

            patientPerson.append(relative)
        # Pre-processing for "NotAvailable" relatives
        # These relatives are typically spouses or other not blood-related relatives
        elif((str)(relative.find('code').get('code'))== "NotAvailable"):
            globalVars.notAvailableRelatives.append(relative) # Add each "NotAvailable" relative to an array
            motherID = 0
            fatherID = 0
            motherFound = False
            fatherFound = False
            relationshipHolder = relative.find(".//relationshipHolder")
            gender = relationshipHolder.find('administrativeGenderCode').get('code')
            id = relationshipHolder.find('id').get('extension')

            if(str(id) == str(newPatientFatherID)):
                relative.find(".//code").set('code', "NFTH")
                relationshipHolder.find('id').set('extension', "3")
                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "6")
                        motherFound = True
                    elif(x.find('code').get('code') == "NFTH"):
                        fatherRelative = x
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "7")
                        fatherFound = True

                # If they do not currently have a mother, add one
                if(motherFound != True):
                    relativeNew = ET.Element('relative', classCode="PRS")
                    ET.SubElement(relativeNew, 'code', code="NMTH")
                    relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                    ET.SubElement(relationshipHolderNew, 'id', extension="6")
                    if(fatherFound):
                        relationshipHolder.insert(relationshipHolder.index(fatherRelative), relativeNew)
                    else:
                        relationshipHolder.append(relativeNew)
                # If they do not currently have a father, add one
                if(fatherFound != True):
                    relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
                    ET.SubElement(relativeNew, 'code', code="NFTH")
                    relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                    ET.SubElement(relationshipHolderNew, 'id', extension="7")

                patientPerson.insert(patientPerson.index(NewFatherRelative),relative)
                patientPerson.remove(NewFatherRelative)

            elif(str(id) == str(newPatientMotherID)):
                motherFound = False
                fatherFound = False

                relative.find(".//code").set('code', "NFTH")
                relationshipHolder.find('id').set('extension', "2")
                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        motherFound = True
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "4")
                    elif(x.find('code').get('code') == "NFTH"):
                        fatherFound = True
                        fatherRelative = x
                        relationshipHolderNew = x.find('relationshipHolder')
                        relationshipHolderNew.find('id').set('extension', "5")
                
                # If they do not currently have a mother, add one
                if(motherFound != True):
                    relativeNew = ET.Element('relative', classCode="PRS")
                    ET.SubElement(relativeNew, 'code', code="NMTH")
                    relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                    ET.SubElement(relationshipHolderNew, 'id', extension="4")
                    if(fatherFound):
                        relationshipHolder.insert(relationshipHolder.index(fatherRelative), relativeNew)
                    else:
                        relationshipHolder.append(relativeNew)
                # If they do not currently have a father, add one
                if(fatherFound != True):
                    relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
                    ET.SubElement(relativeNew, 'code', code="NFTH")
                    relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                    ET.SubElement(relationshipHolderNew, 'id', extension="5")

                patientPerson.insert(patientPerson.index(NewMotherRelative),relative)
                patientPerson.remove(NewMotherRelative)
                
            else:
                motherFound = False
                fatherFound = False
                for x in relationshipHolder.findall(".//relative"):
                    # Check if the "NotAvailable" relative's mother is on the maternal side
                    # If their mother falls in one of the first 7 ids, update accordingly
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        motherID = relationshipHolderNew.find('id').get('extension')
                        if motherID in globalVars.maternalSideIDS:
                            motherFound = True
                        if int(motherID) <= 7 or int(motherID) == int(newPatientOldID):
                            if int(motherID) == 1:
                                relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                            if int(motherID) == 2:
                                relationshipHolderNew.find('id').set('extension', str(OGmotherID))
                            if int(motherID) == 4:
                                if(str(sideOfFamily) == "M"):
                                    relationshipHolderNew.find('id').set('extension', "4")
                                else:
                                    relationshipHolderNew.find('id').set('extension', "6")
                            if int(motherID) == int(newPatientOldID):
                                relationshipHolderNew.find('id').set('extension', "1")  
                    # Check if the "NotAvailable" relative's father is on the maternal side
                    # If their father falls in one of the first 7 ids, update accordingly
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        fatherID = relationshipHolderNew.find('id').get('extension')
                        if fatherID in globalVars.maternalSideIDS:
                            fatherFound = True
                        if int(fatherID) <= 7 or int(fatherID) == int(newPatientOldID):
                            if int(fatherID) == 1:
                                relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                            if int(fatherID) == 3:
                                relationshipHolderNew.find('id').set('extension', str(OGfatherID))
                            if int(fatherID) == 5:
                                if(str(sideOfFamily) == "M"):
                                    relationshipHolderNew.find('id').set('extension', "5")
                                else:
                                    relationshipHolderNew.find('id').set('extension', "7")
                            if int(fatherID) == int(newPatientOldID):
                                relationshipHolderNew.find('id').set('extension', "1")  

                    # If they are on the maternal side, add themselves and their parents to notAvailableIdsToAdd array
                if(motherFound or fatherFound):
                    if(fatherFound and int(motherID) != 0):
                        globalVars.notAvailableIdsToAdd.append(motherID)
                    if(motherFound and int(fatherID) != 0):
                        globalVars.notAvailableIdsToAdd.append(fatherID)
                    globalVars.notAvailableIdsToAdd.append(id)
        elif((str)(relative.find('code').get('code'))[0] != "P"):
            patientPerson.append(relative)


    # Next, we will look at all of the relatives containing the "NotAvailable" code
    # These relatives will only be added if their ID is on the notAvailableIdsToAdd list
    # Note that their might be more IDs on this list than NotAvailable relatives to add.
    # This is because we do not validate if the ID is linked to a NotAvailable relative before it is added,
    # rather, it is a potential list of IDs that should be added if they are NotAvailable.
    # However, since we are only going through relatives that are NotAvailable and have not been added yet,
    # we will not have to worry about duplicating other relatives.
    for x in range(0, len(globalVars.notAvailableRelatives)):
        relative = globalVars.notAvailableRelatives[x]
        # print(relative.find('code').get('code'))
        if((str)(relative.find('code').get('code'))== "NotAvailable"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')
            if(id in globalVars.notAvailableIdsToAdd):
                patientPerson.append(relative)

    # Finally, we will add the original patient's relative and the original mother and father who are now unavailable
    patientPerson.append(OGfather)
    patientPerson.append(OGmother)
    patientPerson.append(originalPatient)


newPatientMotherID = 0
newPatientFatherID = 0