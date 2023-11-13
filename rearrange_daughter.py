import globalVars
from lxml import etree as ET

def determineFamilySide(BeforePatientID):
    global newPatientMotherID
    global newPatientFatherID
    familyside = ""
    for relative in globalVars.relativesArray:
        if((str)(relative.find('code').get('code'))== "DAU"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            if((str)(id) == (str)(BeforePatientID)):
                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        motherID = relationshipHolderNew.find('id').get('extension')
                        newPatientMotherID = motherID
                        if(motherID in globalVars.maternalSideIDS or motherID in globalVars.paternalSideIDS):
                            familyside = "M"
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        fatherID = relationshipHolderNew.find('id').get('extension')
                        newPatientFatherID = fatherID
                        if(fatherID in globalVars.maternalSideIDS or fatherID in globalVars.paternalSideIDS):
                            familyside = "P"

    return familyside

# Create a new relative element to hold the original patient's information.
# Since this function correlates to the rearrange_daughter section, the original
# patient will become a mother or a father.
def makeRelativeForOldPatient(originalPatient):
    # Determine if the old patient will be a daughter or son based on gender
    if(globalVars.originalGender == "F"):
        ET.SubElement(originalPatient, 'code', code = "NMTH")
        patientRelationshipHolder = ET.SubElement(originalPatient, 'relationshipHolder', classCode = "PSN", determinerCode="INSTANCE")
        ET.SubElement(patientRelationshipHolder, 'id', extension = "2")
        originalPatientID = 2
    else:
        ET.SubElement(originalPatient, 'code', code = "NFTH")
        patientRelationshipHolder = ET.SubElement(originalPatient, 'relationshipHolder', classCode = "PSN", determinerCode="INSTANCE")
        ET.SubElement(patientRelationshipHolder, 'id', extension = "3")
        originalPatientID = 3
    
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
    
    # Make the oldPatient's mother a grandmother
    # Paternal/Maternal will be determined by looking at the originalPatient's gender
    GRMTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    if(originalPatientID == 2):
        ET.SubElement(GRMTHRelative, 'code', code = "NMTH")
        relationshipHolderNew = ET.SubElement(GRMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="4")     # give the old patient the correct grandmother
    else:
        ET.SubElement(GRMTHRelative, 'code', code = "NMTH")
        relationshipHolderNew = ET.SubElement(GRMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="6")     # give the old patient the correct grandmother
    
    # Make the oldPatient's father a grandfather
    # Paternal/Maternal will be determined by looking at the originalPatient's gender
    GRFTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    
    if(originalPatientID == 2):
        ET.SubElement(GRFTHRelative, 'code', code = "NFTH")
        relationshipHolderNew = ET.SubElement(GRFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="5") # give the old patient the correct grandfather
    else:
        ET.SubElement(GRFTHRelative, 'code', code = "NFTH")
        relationshipHolderNew = ET.SubElement(GRFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="7") # give the old patient the correct grandfather

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
def rearrange(tree, patientPerson, BeforePatientID):
    global newPatientFatherID
    global newPatientMotherID
    sideOfFamily = determineFamilySide(BeforePatientID)

    mgrmthCode = (int)(globalVars.currentMaxId) + 1
    mgrfthCode = (int)(globalVars.currentMaxId) + 2
    pgrmthCode = (int)(globalVars.currentMaxId) + 3
    pgrfthCode = (int)(globalVars.currentMaxId) + 4
    # Any new relatives to be added will start with lowest unused id
    currentId = (int)(globalVars.currentMaxId) + 5

    # variables to find the spouse's ID
    spouseIDfound = False
    spouseID = 1

    # Create a new relative element for the original patient
    originalPatient = ET.Element('relative', classCode = "PRS")
    originalPatientID = makeRelativeForOldPatient(originalPatient)

    # The first 6 members of the family will be dealt with first.
    # This includes the mother, father, maternal grandmother, and maternal grandfather
    for x in range(6):
        relative = globalVars.relativesArray[x]
        # print(relative.find('code').get('code'))

        # Maternal Grandmother -> (M/P) great grandmother
        if((str)(relative.find('code').get('code'))== "MGRMTH"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "GGRMTH"))
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(mgrmthCode)) 
            ogmgrmth = relative
        # Maternal Grandfather -> (M/P) great grandfather
        elif((str)(relative.find('code').get('code'))== "MGRFTH"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "GGRFTH"))
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(mgrfthCode))
            ogmgrfth = relative
        # Paternal Grandmother -> (M/P) great grandmother
        elif((str)(relative.find('code').get('code'))== "PGRMTH"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "GGRMTH"))
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(pgrmthCode))
            ogpgrmth = relative
        # Paternal Grandfather -> (M/P) great grandfather
        elif((str)(relative.find('code').get('code'))== "PGRFTH"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "GGRFTH"))
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(pgrfthCode))
            ogpgrfth = relative
        # Father -> (M/P) Grandfather 
        elif((str)(relative.find(".//code").get('code')) == "NFTH"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "GRFTH"))
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since we are essentially creating a new relative, we need a completely new ID
            if(originalPatientID == 2):
                relationshipHolder.find(".//id").set('extension',"5") 
            else:
                relationshipHolder.find(".//id").set('extension',"7") 

            # We need to update the original patient's parents to be the same as the new patient's
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(pgrmthCode))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(pgrfthCode)) 

            # Note that we are creating a new relative (father) that will be added to the HL7 later
            # rather than being appending now
            OGfather = relative
        # Mother -> (M/P) Grandmother
        elif((str)(relative.find(".//code").get('code')) == "NMTH"):
            # The original patient's mother becomes the new patient's sister
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "GRMTH"))
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since we are essentially creating a new relative, we need a completely new ID
            if(originalPatientID == 2):
                relationshipHolder.find(".//id").set('extension',"4") 
            else:
                relationshipHolder.find(".//id").set('extension',"6") 

            # We need to update the original patient's parents to be the same as the new patient's
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(mgrmthCode))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(mgrfthCode)) 

            # Note that we are creating a new relative (mother) that will be added to the HL7 later
            # rather than being appending now
            OGmother = relative


    # add the new mother if the old patient was female
    if(originalPatientID == 2):
        patientPerson.append(originalPatient)

        # add father to update later
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
    else:
        # add mother to update later
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

        patientPerson.append(originalPatient)

    # Make grandparents, either the maternal or paternal side
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

        patientPerson.append(OGmother)
        patientPerson.append(OGfather)

    else:
        patientPerson.append(OGmother)
        patientPerson.append(OGfather)

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

    # The first 6 members of the family will be dealt with first.
    # This includes the mother, father, maternal grandmother, and maternal grandfather
    # The paternal grandmother and paternal grandfather are also included in these 6 relatives
    for x in range(6, len(globalVars.relativesArray)):
        relative = globalVars.relativesArray[x]

        # Sister -> Aunt (Paternal or Maternal TBD)
        if((str)(relative.find('code').get('code'))== "NSIS"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "AUNT")) # auto makes aunt paternal or maternal
            relationshipHolder = relative.find(".//relationshipHolder")

            # Fix the parent ids from their current #2 and #3 to #4-7
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"): # update NMTH to the correct grandmotherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', "4")
                    else: 
                        relationshipHolderNew.find('id').set('extension', "6")
                elif(x.find('code').get('code') == "NFTH"): # update NFTH to the correct grandfatherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', "5")
                    else: 
                        relationshipHolderNew.find('id').set('extension', "7")
            patientPerson.append(relative)

        # Brother -> Uncle (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NBRO"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "UNCLE")) # auto makes uncle paternal or maternal
            relationshipHolder = relative.find(".//relationshipHolder")

            # Fix the parent ids from their current #2 and #3 to #4-7
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"): # update NMTH to the correct grandmotherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', "4")
                    else: 
                        relationshipHolderNew.find('id').set('extension', "6")
                elif(x.find('code').get('code') == "NFTH"): # update NFTH to the correct grandfatherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', "5")
                    else: 
                        relationshipHolderNew.find('id').set('extension', "7")
            patientPerson.append(relative)

        # Maternal Aunt -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "MAUNT"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            relationshipHolder = relative.find(".//relationshipHolder")

            # Link mother -> og mgrmth
            # Link father -> og mgrfth
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(mgrmthCode))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(mgrfthCode))

            patientPerson.append(relative)

        # Paternal Aunt -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "PAUNT"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            relationshipHolder = relative.find(".//relationshipHolder")

            # Link mother -> og pgrmth
            # Link father -> og pgrfth
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(pgrmthCode))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(pgrfthCode))

            patientPerson.append(relative)

        # Maternal Uncle -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "MUNCLE"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            relationshipHolder = relative.find(".//relationshipHolder")

            # Link mother -> og mgrmth
            # Link father -> og mgrfth
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(mgrmthCode))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(mgrfthCode))
            
            patientPerson.append(relative)

        # Paternal Uncle -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "PUNCLE"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            relationshipHolder = relative.find(".//relationshipHolder")

            # Link mother -> og pgrmth
            # Link father -> og pgrfth
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(pgrmthCode))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(pgrfthCode))
            
            patientPerson.append(relative)

        # Niece -> Cousin (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NIECE"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "COUSN")) # auto makes cousin paternal or maternal
            
            # add parents to NotAvailable array
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

        # Nephew -> Cousin (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NEPHEW"):
            relative.find(".//code").set('code', ((str)(sideOfFamily) + "COUSN")) # auto makes cousin paternal or maternal
            
            # add parents to NotAvailable array
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

        # Maternal Cousin -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "MCOUSN"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            
            # add parents to NotAvailable array
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

        # Paternal Cousin -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "PCOUSN"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            
            # add parents to NotAvailable array
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

        # Cousin -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "COUSN"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            
            # add parents to NotAvailable array
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

        # Daughter -> Sister / Patient
        elif((str)(relative.find('code').get('code'))== "DAU"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            # If they are the patient, we will collect their subjectOf1 and subjectOf2 data 
            # Then we will move on to the next patient as they do not need to be added as a relative
            if((str)(id) == (str)(BeforePatientID)):
                # Since the new patient is the daughter, we must collect some data about her that will be
                # added later in main.py after rearrangment
                for subjectOf1Data in relative.findall('.//subjectOf1'):
                    globalVars.newPatientSubjectOf1.append(subjectOf1Data)
                for subjectOf2Data in relative.findall('.//subjectOf2'):
                    globalVars.newPatientSubjectOf1.append(subjectOf2Data)
                continue
            else:
                relative.find(".//code").set('code', "NSIS") # update to sister if not the new patient

            relationshipHolder = relative.find(".//relationshipHolder")

            # Link sister -> mother and father same as new patient
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    tempID = relationshipHolderNew.find('id').get('extension')
                    if(~spouseIDfound & tempID != "1"): #if the mother isn't the patient then get ID
                        spouseID = tempID
                        spouseIDfound = True
                    relationshipHolderNew.find('id').set('extension', "2")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    tempID = relationshipHolderNew.find('id').get('extension')
                    if(~spouseIDfound & tempID != "1"): #if the father isn't the patient then get ID
                        spouseID = tempID
                        spouseIDfound = True
                    relationshipHolderNew.find('id').set('extension', "3")

            patientPerson.append(relative)

        # Son -> Brother
        elif((str)(relative.find('code').get('code'))== "SON"):
            relative.find(".//code").set('code', "NBRO")
            relationshipHolder = relative.find(".//relationshipHolder")

            # Link brother -> mother and father same as new patient
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    tempID = relationshipHolderNew.find('id').get('extension')
                    if(~spouseIDfound & tempID != "1"): #if the mother isn't the patient then get ID
                        spouseID = tempID
                        spouseIDfound = True
                    relationshipHolderNew.find('id').set('extension', "2")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    tempID = relationshipHolderNew.find('id').get('extension')
                    if(~spouseIDfound & tempID != "1"): #if the mother isn't the patient then get ID
                        spouseID = tempID
                        spouseIDfound = True
                    relationshipHolderNew.find('id').set('extension', "3")
            patientPerson.append(relative)

        # Grandchildren -> (niece/nephew) OR (son/daughter)
        # if the daughter is the new patient then change ID
        elif((str)(relative.find('code').get('code'))== "GRNDDAU"):
            relationshipHolder = relative.find(".//relationshipHolder")
            child = False
            
            #it is rearrange_daughter so if grandchild mother is the new patient, change ID
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                    if(motherID == BeforePatientID): # change id of mother to patientID if her id matches BeforePatientID
                        relationshipHolderNew.find('id').set('extension', "1")
                        child = True
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(fatherID)
            
            # Determine sis or niece based on parents
            if(child == False):
                relative.find(".//code").set('code', "NIECE")
            elif(child == True):
                relative.find(".//code").set('code', "DAU")

            patientPerson.append(relative)

        elif((str)(relative.find('code').get('code'))== "GRNDSON"):
            relationshipHolder = relative.find(".//relationshipHolder")
            child = False
            
            #it is rearrange_daughter so if grandchild mother is the new patient, change ID
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                    if(motherID == BeforePatientID): # change id of mother to patientID if her id matches BeforePatientID
                        relationshipHolderNew.find('id').set('extension', "1")
                        child = True
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                    
            # Determine bro or nephew based on parents
            if(child == False):
                relative.find(".//code").set('code', "NEPHEW")
            elif(child == True):
                relative.find(".//code").set('code', "SON")

            patientPerson.append(relative)

        # Great-Grandmother -> not available
        elif((str)(relative.find('code').get('code'))== "MGGRMTH" or (str)(relative.find('code').get('code'))== "PGGRMTH"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")

            patientPerson.append(relative)

        # Great-Grandfather -> not available
        elif((str)(relative.find('code').get('code'))== "MGGRFTH" or (str)(relative.find('code').get('code'))== "PGGRFTH"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")

            patientPerson.append(relative)

        # need the spouse id from the Old patient to change from "NotAvailable"
        # to NFTH, then create the side of grandparents that are missing
        elif((str)(relative.find('code').get('code'))== "NotAvailable"):
            globalVars.notAvailableRelatives.append(relative) # Add each "NotAvailable" relative to an array
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')
            motherFound = False
            fatherFound = False

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
                for x in relationshipHolder.findall(".//relative"):
                    # Check if the "NotAvailable" relative's mother is on the maternal side
                    # If their mother falls in one of the first 7 ids, update accordingly
                    if(x.find('code').get('code') == "NMTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        motherID = relationshipHolderNew.find('id').get('extension')
                        globalVars.notAvailableIdsToAdd.append(motherID)
                        if int(motherID) <= 7 or int(motherID) == int(BeforePatientID):
                            if int(motherID) == 1:
                                relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                            if int(motherID) == 2:
                                if(sideOfFamily == "M"):
                                    relationshipHolderNew.find('id').set('extension', "4")
                                else:
                                    relationshipHolderNew.find('id').set('extension', "6")
                            if int(motherID) == 4:
                                relationshipHolderNew.find('id').set('extension', str(mgrmthCode))  
                            if int(motherID) == 6:
                                relationshipHolderNew.find('id').set('extension', str(pgrmthCode))  
                            if int(motherID) == int(BeforePatientID):
                                relationshipHolderNew.find('id').set('extension', "1")  
                    # Check if the "NotAvailable" relative's father is on the maternal side
                    # If their father falls in one of the first 7 ids, update accordingly
                    elif(x.find('code').get('code') == "NFTH"):
                        relationshipHolderNew = x.find('relationshipHolder')
                        fatherID = relationshipHolderNew.find('id').get('extension')
                        globalVars.notAvailableIdsToAdd.append(fatherID)
                        if int(fatherID) <= 7 or int(fatherID) == int(BeforePatientID):
                            if int(fatherID) == 1:
                                relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                            if int(fatherID) == 3:
                                if(sideOfFamily == "M"):
                                    relationshipHolderNew.find('id').set('extension', "5")
                                else:
                                    relationshipHolderNew.find('id').set('extension', "7")
                            if int(fatherID) == 5:
                                relationshipHolderNew.find('id').set('extension', str(mgrfthCode)) 
                            if int(fatherID) == 7:
                                relationshipHolderNew.find('id').set('extension', str(pgrfthCode)) 
                            if int(fatherID) == int(BeforePatientID):
                                relationshipHolderNew.find('id').set('extension', "1")  

                globalVars.notAvailableIdsToAdd.append(id)
        else:
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

    # Finally, we will add the original patient's relative that was created earlier and the og grandparents who are now unavailable
    patientPerson.append(ogmgrmth)
    patientPerson.append(ogmgrfth)
    patientPerson.append(ogpgrmth)
    patientPerson.append(ogpgrfth)

newPatientMotherID = 0
newPatientFatherID = 0