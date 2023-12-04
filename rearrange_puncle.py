import globalVars
from lxml import etree as ET

# Create a new relative element to hold the original patient's information.
# Since this function correlates to the rearrange_maunt section, the original
# patient will become a NIECE or nephew
def makeRelativeForOldPatient(originalPatient, fatherId, motherId, currentId):
    # Determine if the old patient will be a NIECE or nephew on gender
    if(globalVars.originalGender == "F"):
        ET.SubElement(originalPatient, 'code', code = "NIECE")
    else:
        ET.SubElement(originalPatient, 'code', code = "NEPHEW")
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
    ET.SubElement(relationshipHolderNew, 'id', extension=str(motherId))     # Update the original patient's mother id to reflect her new id
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
    currentId = (int)(globalVars.currentMaxID) + 1 # Any new relatives to be added will start with the next available ID

    # The first 6 members of the family will be dealt with first.
    # This includes the mother, father, paternal grandmother, and paternal grandfather
    # The maternal grandmother and maternal grandfather are also included in these 6 relatives,
    # however, as they are not on the paternal side of the family they will not be dealt with.
    for x in range(6):
        relative = globalVars.relativesArray[x]
        # print(relative.find('code').get('code'))

        # Paternal Grandmother -> Mother
        if((str)(relative.find('code').get('code'))== "PGRMTH"):
            relative.find(".//code").set('code', "NMTH") # Update to mother code
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', "2") # Update to mother ID

            motherFound = False
            fatherFound = False
            PGRMTHMotherID = 0
            PGRMTHFatherID = 0

            # Look to see if MGRMTH has any parents (original patient's great-grandparents)
            # If they do, not the ID that they currently hold
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    PGRMTHMotherID = relationshipHolderNew.find('id').get('extension')
                    relationshipHolderNew.find('id').set('extension', "4")
                    motherFound = True
                elif(x.find('code').get('code') == "NFTH"):
                    fatherRelative = x
                    relationshipHolderNew = x.find('relationshipHolder')
                    PGRMTHFatherID = relationshipHolderNew.find('id').get('extension')
                    relationshipHolderNew.find('id').set('extension', "5")
                    fatherFound = True

            
            # They first 7 ids are fixed and must be present, so as we move up we must create
            # grandparents for the new patient if they are not already present as great-grandparents
            # They will become the new maternal grandmother and maternal grandfather

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

            patientPerson.append(relative)
        # Paternal Grandfather -> Father
        elif((str)(relative.find('code').get('code'))== "MGRFTH"):
            relative.find(".//code").set('code', "NFTH") # Update to father code
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', "3") # Update to father code

            motherFound = False
            fatherFound = False
            PGRFTHMotherID = 0
            PGRFTHFatherID = 0
            # Look to see if MGRFTH has any parents (original patient's great-grandparents)
            # If they do, note the ID that they currently hold
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    PGRFTHMotherID = relationshipHolderNew.find('id').get('extension')
                    relationshipHolderNew.find('id').set('extension', "6")
                    motherFound = True
                elif(x.find('code').get('code') == "NFTH"):
                    fatherRelative = x
                    relationshipHolderNew = x.find('relationshipHolder')
                    PGRFTHFatherID = relationshipHolderNew.find('id').get('extension')
                    relationshipHolderNew.find('id').set('extension', "7")
                    fatherFound = True

            # They first 7 ids are fixed and must be present, so as we move up we must create
            # grandparents for the new patient if they are not already present as great-grandparents
            # They will become the new paternal grandmother and paternal grandfather

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

            patientPerson.append(relative)
        elif((str)(relative.find(".//code").get('code')) == "NMTH"):
            # The original patient's mother becomes the new patient's sister-in-law labeling her "NotAvailable"
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since we are essentially creating a new relative, we need a completely new ID
            relationshipHolder.find(".//id").set('extension', str(currentId)) 
            OGmotherID = currentId
            currentId += 1
            # The original patient's mother will have parent's (PGRMTH and PGRFTH)
            # Since they will not be in the new pedigree, we must remove them
            for x in relationshipHolder.findall(".//relative"):
                relationshipHolder.remove(x)

            # Note that we are creating a new relative (mother) that will be added to the HL7 later
            # rather than being appending now
            OGMother = relative
        elif((str)(relative.find(".//code").get('code')) == "NFTH"):
            # The original patient's father becomes the new patient's sister
            relative.find(".//code").set('code', "NBRO")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since we are essentially creating a new relative, we need a completely new ID
            relationshipHolder.find(".//id").set('extension', str(currentId)) 
            OGfatherID = currentId
            currentId += 1
            # We need to update the original patient's parents to be the same as the new patient's
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "2")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "3") 

            # Note that we are creating a new relative (father) that will be added to the HL7 later
            # rather than being appending now
            OGFather = relative

    # Create a new relative element for the original patient
    # This action is completed here to ensure that the original patient's father's ID has already been created
    originalPatient = ET.Element('relative', classCode = "PRS")
    originalPatientID = makeRelativeForOldPatient(originalPatient, OGfatherID, OGmotherID, currentId)
    currentId += 1

    # Create new grandparents. These will be updated if the original patient had great-grandparents. Otherwise, they will stay blank.
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

        # Sister -> NIECE
        if((str)(relative.find('code').get('code'))== "NSIS"):
            relative.find(".//code").set('code', "NIECE")
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

        # Brother -> Nephew
        elif((str)(relative.find('code').get('code'))== "NBRO"):
            relative.find(".//code").set('code', "NEPHEW")
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

        # Paternal Aunt -> Sister
        elif((str)(relative.find('code').get('code'))== "PAUNT"):
            relationshipHolder = relative.find(".//relationshipHolder")

            relative.find(".//code").set('code', "NSIS")
            # Link mother -> mother id (2)
            # Link father -> father id (3)
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "2")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "3")

            patientPerson.append(relative)
        # Paternal Uncle -> Brother
        elif((str)(relative.find('code').get('code'))== "PUNCLE"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            # If they are the patient, we will collect their subjectOf1 and subjectOf2 data 
            # Then we will move on to the next patient as they do not need to be added as a relative
            if((str)(id) == (str)(newPatientOldID)):
                # Since the new patient is the paternal uncle, we must collect some data about her that will be
                # added later in main.py after rearrangment
                for subjectOf1Data in relative.findall('.//subjectOf1'):
                    globalVars.newPatientSubjectOf1.append(subjectOf1Data)
                for subjectOf2Data in relative.findall('.//subjectOf2'):
                    globalVars.newPatientSubjectOf1.append(subjectOf2Data)
                continue

            relative.find(".//code").set('code', "NBRO")
            # Link mother -> mother id (2)
            # Link father -> father id (3)
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "2")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "3")

            patientPerson.append(relative)
        # Niece -> Not Available
        elif((str)(relative.find('code').get('code'))== "NIECE"):
            motherID = 0
            fatherID = 0
            motherFound = False
            fatherFound = False
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since "NIECE" is not defined as being maternal or paternal, we have to take
            # an extra step to determine if they should be included in the new patient's pedigree
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    # Check if mother is on the paternal side
                    if motherID in globalVars.paternalSideIDS:
                        motherFound = True
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    # Check if father is on the paternal side
                    if fatherID in globalVars.paternalSideIDS:
                        fatherFound = True

            # If they have a relative on the paternal side (mother or father), they will be added to the pedigree
            # If this is the case, then we will also add the spouse's ID (if their father is related, we will add the mother) 
            # to an array that is keeping track of "Not Available" relatives that should be added to pedigree as well.
            if(motherFound or fatherFound):
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                patientPerson.append(relative)

        #Nephew -> Not Available
        elif((str)(relative.find('code').get('code'))== "NEPHEW"):
            motherID = 0
            fatherID = 0
            motherFound = False
            fatherFound = False
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since "NEPHEW" is not defined as being maternal or paternal, we have to take
            # an extra step to determine if they should be included in the new patient's pedigree
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    # Check if mother is on the paternal side
                    if motherID in globalVars.paternalSideIDS:
                        motherFound = True
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    # Check if father is on the paternal side
                    if fatherID in globalVars.paternalSideIDS:
                        fatherFound = True

            # If they have a relative on the paternal side (mother or father), they will be added to the pedigree
            # If this is the case, then we will also add the spouse's ID (if their father is related, we will add the mother) 
            # to an array that is keeping track of "Not Available" relatives that should be added to pedigree as well.
            if(motherFound or fatherFound):
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                patientPerson.append(relative)

        # Paternal Cousin -> Niece/Nephew, or Son/Daughter depending on parent
        elif((str)(relative.find('code').get('code'))== "PCOUSN"):
            relationshipHolder = relative.find(".//relationshipHolder")
            gender = relationshipHolder.find('administrativeGenderCode').get('code')
            child = False

            # In case one of their parents is "Not Available", we will add both to our 'notAvailableIdsToAdd' array
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    if((str)(fatherID) == (str)(newPatientOldID)):
                        relationshipHolderNew.find('id').set('extension',"1")
                        child = True
                    globalVars.notAvailableIdsToAdd.append(fatherID)

            # Determine niece/nephew or son/daughter depending on gender
            if(gender == "F"):
                if(child == False):
                    relative.find(".//code").set('code', "NIECE")
                elif(child == True):
                    relative.find(".//code").set('code', "DAU")
            else:
                if(child == False):
                    relative.find(".//code").set('code', "NEPHEW")
                elif(child == True):
                    relative.find(".//code").set('code', "SON")

            patientPerson.append(relative)

        # Daughter -> Not Available
        elif((str)(relative.find('code').get('code'))== "DAU"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")

            # In case one of their parents is "Not Available", we will add both to our 'notAvailableIdsToAdd' array
            # Since the mother or the father will have been the original patient, we will want to update their corresponding link
            # to the new ID that we created for the original patient
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                    if(motherID == "1"):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                    if(fatherID == "1"):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
            patientPerson.append(relative)
        # Son -> NotAvailable
        elif((str)(relative.find('code').get('code'))== "SON"):
            relative.find(".//code").set('code', "NotAvaiable")
            relationshipHolder = relative.find(".//relationshipHolder")

            # In case one of their parents is "Not Available", we will add both to our 'notAvailableIdsToAdd' array
            # Since the mother or the father will have been the original patient, we will want to update their corresponding link
            # to the new ID that we created for the original patient
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(motherID)
                    if(motherID == "1"):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                    if(fatherID == "1"):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
            patientPerson.append(relative)
        #Granddaughter -> Not Available
        elif((str)(relative.find('code').get('code'))== "GRNDDAU"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")

            # In case one of their parents is "Not Available", we will add both to our 'notAvailableIdsToAdd' array
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
        # Grandson -> Not Available
        elif((str)(relative.find('code').get('code'))== "GRNDSON"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")

            # In case one of their parents is "Not Available", we will add both to our 'notAvailableIdsToAdd' array
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
        # Paternal Great-Grandmother -> M or P GRMTH
        elif((str)(relative.find('code').get('code'))== "PGGRMTH"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')

            # if the MGGRMTH's ID matches the original paternal grandmother mother's id, she will be the new maternal grandmother
            if(id == PGRMTHMotherID):
                relative.find(".//code").set('code', "MGRMTH")
                relationshipHolder.find('id').set('extension', "4")
                patientPerson.insert(patientPerson.index(MGRMTHRelative),relative)
                patientPerson.remove(MGRMTHRelative)
            # if the MGGRMTH's ID matches the original paternal grandfather mother's id, she will be the new paternal grandmother
            elif(id == PGRFTHMotherID):
                relative.find(".//code").set('code', "PGRMTH")
                relationshipHolder.find('id').set('extension', "6")
                patientPerson.insert(patientPerson.index(PGRMTHRelative),relative)
                patientPerson.remove(PGRMTHRelative)
        # Paternal Great-Grandfather -> M or P GRFTH
        elif((str)(relative.find('code').get('code'))== "PGGRFTH"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')

            # if the MGGRFTH's ID matches the original paternal grandmother father's id, he will be the new maternal grandfather
            if(id == PGRMTHFatherID):
                relative.find(".//code").set('code', "MGRFTH")
                relationshipHolder.find('id').set('extension', "5")
                patientPerson.insert(patientPerson.index(MGRFTHRelative),relative)
                patientPerson.remove(MGRFTHRelative)
            # if the MGGRFTH's ID matches the original paternal grandfather father's id, he will be the new paternal grandfather
            elif(id == PGRFTHFatherID):
                relative.find(".//code").set('code', "PGRFTH")
                relationshipHolder.find('id').set('extension', "7")
                patientPerson.insert(patientPerson.index(PGRFTHRelative),relative)
                patientPerson.remove(PGRFTHRelative)
        # Pre-processing for "NotAvailable" relatives
        # These relatives are typically spouses or other not blood-related relatives
        # Since they do not fall onto the maternal or paternal side naturally, we have to manually check
        elif((str)(relative.find('code').get('code'))== "NotAvailable"):
            globalVars.notAvailableRelatives.append(relative) # Add each "NotAvailable" relative to an array
            motherFound = False
            fatherFound = False
            motherID = 0
            fatherID = 0
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')

            for x in relationshipHolder.findall(".//relative"):
                # Check if the "NotAvailable" relative's mother is on the paternal side
                # If their mother falls in one of the first 7 ids, update accordingly
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    if motherID in globalVars.paternalSideIDS:
                        motherFound = True
                    if int(motherID) <= 7 or int(motherID) == int(newPatientOldID):
                        if int(motherID) == 1:
                            relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                        if int(motherID) == 2:
                            relationshipHolderNew.find('id').set('extension', str(OGmotherID))
                        if int(motherID) == 6:
                            relationshipHolderNew.find('id').set('extension', "2") 
                        if int(motherID) == int(newPatientOldID):
                            relationshipHolderNew.find('id').set('extension', "1")    
                # Check if the "NotAvailable" relative's father is on the paternal side
                # If their father falls in one of the first 7 ids, update accordingly
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    if fatherID in globalVars.paternalSideIDS:
                        fatherFound = True
                    if int(fatherID) <= 7 or int(fatherID) == int(newPatientOldID):
                        if int(fatherID) == 1:
                            relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                        if int(fatherID) == 3:
                            relationshipHolderNew.find('id').set('extension', str(OGfatherID))
                        if int(fatherID) == 7:
                            relationshipHolderNew.find('id').set('extension', "3") 
                        if int(fatherID) == int(newPatientOldID):
                            relationshipHolderNew.find('id').set('extension', "1")  
            
            # If they are on the paternal side, add themselves and their parents to notAvailableIdsToAdd array
            if(motherFound or fatherFound):
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                globalVars.notAvailableIdsToAdd.append(id)
        elif((str)(relative.find('code').get('code'))[0] != "M"):
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

    # Finally, we will add the father relative (new patient's brother-in-law), the mother relative (new patient's sister),
    # and the original patient's relative that was created earlier
    patientPerson.append(OGMother)
    patientPerson.append(OGFather)
    patientPerson.append(originalPatient)