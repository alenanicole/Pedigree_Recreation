import globalVars
from lxml import etree as ET

# Create a new relative element to hold the original patient's information.
# Since this function correlates to the rearrange_mgrnmother section, the original
# patient will become a granddaughter or grandson.
def makeRelativeForOldPatient(originalPatient, fatherId, motherId, currentId):
    # Determine if the old patient will be a daughter or son based on gender
    if(globalVars.originalGender == "F"):
        ET.SubElement(originalPatient, 'code', code = "GRNDDAU")
    else:
        ET.SubElement(originalPatient, 'code', code = "GRNDSON")
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
    ET.SubElement(relationshipHolderNew, 'id', extension=str(motherId))    # Update the original patient's father id to reflect his new id
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
def rearrange(tree, patientPerson):
    currentId = 100 # Any new relatives to be added will start with the ID of 100
    grandmotherId = 99

    # The first 6 members of the family will be dealt with first.
    # This includes the mother, father, maternal grandmother, and maternal grandfather
    # The paternal grandmother and paternal grandfather are also included in these 6 relatives,
    # however, as they are not on the maternal side of the family they will not be dealt with.
    for x in range(6):
        relative = globalVars.relativesArray[x]
        # print(relative.find('code').get('code'))

        # Maternal Grandfather -> Patient
        if((str)(relative.find('code').get('code'))== "MGRFTH"):
            # Since the new patient is the maternal grandfather, we must collect some data about him that will be
            # added later in main.py after rearrangment
            for subjectOf1Data in relative.findall('.//subjectOf1'):
                globalVars.newPatientSubjectOf1.append(subjectOf1Data)
            for subjectOf2Data in relative.findall('.//subjectOf2'):
                globalVars.newPatientSubjectOf1.append(subjectOf2Data)
            
            relationshipHolder = relative.find(".//relationshipHolder")
            MGRFTHMotherID = 0
            MGRFTHFatherID = 0

            # Look to see if MGRMTH has any parents (original patient's great-grandparents)
            # If they do, not the ID that they currently hold
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    MGRFTHMotherID = relationshipHolderNew.find('id').get('extension')
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    MGRFTHFatherID = relationshipHolderNew.find('id').get('extension')


        # Maternal Grandmother -> Spouse
        elif((str)(relative.find('code').get('code'))== "MGRMTH"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(grandmotherId))

            # Since the new patient's inlaws will not be in the new pedigree, we must remove them
            for x in relationshipHolder.findall(".//relative"):
                relationshipHolder.remove(x)


            grandmother = relative
        # Father -> Not Available
        elif((str)(relative.find(".//code").get('code')) == "NFTH"):
            # The original patient's father is not related to the maternal grandmother, labeling him "NotAvailable"
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since we are essentially creating a new relative, we need a completely new ID
            relationshipHolder.find(".//id").set('extension', str(currentId)) 
            OGfatherID = currentId
            currentId += 1
            # The original patient's father will have parent's (PGRMTH and PGRFTH)
            # Since they will not be in the new pedigree, we must remove them
            for x in relationshipHolder.findall(".//relative"):
                relationshipHolder.remove(x)

            # Note that we are creating a new relative (father) that will be added to the HL7 later
            # rather than being appending now
            OGfather = relative
        # Mother -> Daughter
        elif((str)(relative.find(".//code").get('code')) == "NMTH"):
            relative.find(".//code").set('code', "DAU")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(currentId)) 
            OGmotherID = currentId
            currentId += 1
 
            # Link mother -> new relative created for father
            # Link father -> new patient
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension',  str(grandmotherId))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "1") 

            OGmother = relative

    
    # Create a new relative element for the original patient
    # This action is completed here to ensure that the original patient's father's ID has already been created
    originalPatient = ET.Element('relative', classCode = "PRS")
    originalPatientID = makeRelativeForOldPatient(originalPatient, OGfatherID, OGmotherID, currentId)
    currentId += 1

    # Create new parents (if the original patient had great grandparents, these will be updated)
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

    # Create new grandparents.
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

        # Sister -> Granddaughter
        if((str)(relative.find('code').get('code'))== "NSIS"):
            relative.find(".//code").set('code', "GRNDDAU")
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

        # Brother -> Grandson
        elif((str)(relative.find('code').get('code'))== "NBRO"):
            relative.find(".//code").set('code', "GRNDSON")
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

        # Maternal Aunt -> Daughter
        elif((str)(relative.find('code').get('code'))== "MAUNT"):
            relative.find(".//code").set('code', "DAU")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Link mother -> mother id (1)
            # Link father -> father id (grandfatherId)
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(grandmotherId))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "1")

            patientPerson.append(relative)
        # Maternal Uncle -> SON
        elif((str)(relative.find('code').get('code'))== "MUNCLE"):
            relative.find(".//code").set('code', "SON")
            relationshipHolder = relative.find(".//relationshipHolder")
            # Link mother -> mother id (1)
            # Link father -> father id (grandfatherID)
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(grandmotherId))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "1")

            patientPerson.append(relative)
        # Niece -> Not Available
        elif((str)(relative.find('code').get('code'))== "NIECE"):
            motherID = 0
            fatherID = 0
            motherFound = False
            fatherFound = False
            unknown = True
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since "NIECE" is not defined as being maternal or paternal, we have to take
            # an extra step to determine if they should be included in the new patient's pedigree
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    # Check if mother is on the maternal side
                    if motherID in globalVars.maternalSideIDS:
                        motherFound = True
                        unknown = False
                    elif motherID in globalVars.paternalSideIDS:
                        unknown = False
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    # Check if father is on the maternal side
                    if fatherID in globalVars.maternalSideIDS:
                        fatherFound = True
                        unkown = False
                    elif motherID in globalVars.paternalSideIDS:
                        unknown = False

            # If they have a relative on the maternal side (mother or father), they will be added to the pedigree
            # If this is the case, then we will also add the spouse's ID (if their father is related, we will add the mother) 
            # to an array that is keeping track of "Not Available" relatives that should be added to pedigree as well.
            if(motherFound or fatherFound):
                relative.find(".//code").set('code', "NotAvailable")
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                patientPerson.append(relative)
            elif(unknown):
                patientPerson.apppend(relative)

        # Nephew -> Not Available
        elif((str)(relative.find('code').get('code'))== "NEPHEW"):
            motherID = 0
            fatherID = 0
            motherFound = False
            fatherFound = False
            unknown = True
            relationshipHolder = relative.find(".//relationshipHolder")
            # Since "NEPHEW" is not defined as being maternal or paternal, we have to take
            # an extra step to determine if they should be included in the new patient's pedigree
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    # Check if mother is on the maternal side
                    if motherID in globalVars.maternalSideIDS:
                        motherFound = True
                        unknown = False
                    elif motherID in globalVars.paternalSideIDS:
                        unknown = False
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    # Check if father is on the maternal side
                    if fatherID in globalVars.maternalSideIDS:
                        fatherFound = True
                        unknown = False
                    elif motherID in globalVars.paternalSideIDS:
                        unknown = False

            # If they have a relative on the maternal side (mother or father), they will be added to the pedigree
            # If this is the case, then we will also add the spouse's ID (if their father is related, we will add the mother) 
            # to an array that is keeping track of "Not Available" relatives that should be added to pedigree as well.
            if(motherFound or fatherFound):
                relative.find(".//code").set('code', "NotAvailable")
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                patientPerson.append(relative)
            elif(unknown):
                patientPerson.append(relative)
        # Maternal Cousin -> granddaughter or grandson
        elif((str)(relative.find('code').get('code'))== "MCOUSN"):
            relationshipHolder = relative.find(".//relationshipHolder")
            gender = relationshipHolder.find('administrativeGenderCode').get('code')
            # Determine granddaughter or grandson depending on gender
            if(gender == "F"):
                relative.find(".//code").set('code', "GRNDDAU")
            else:
                relative.find(".//code").set('code', "GRNDSON")

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
        # Son -> Not Available
        elif((str)(relative.find('code').get('code'))== "SON"):
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
        # Granddaughter -> Not Available
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
        # Maternal Great-Grandmother -> mother
        elif((str)(relative.find('code').get('code'))== "MGGRMTH"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')

            # if the MGGRMTH's ID matches the original maternal grandmother mother's id, she will be the new mother
            if(id == MGRFTHMotherID):
                relative.find(".//code").set('code', "NMTH")
                relationshipHolder.find('id').set('extension', "2")

                mother = ET.SubElement(relationshipHolder, 'relative', classCode = "PRS")
                ET.SubElement(mother, 'code', code="NMTH")
                relationshipHolderMother = ET.SubElement(mother, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderMother, 'id', extension="4")
                father = ET.SubElement(relationshipHolder, 'relative', classCode = "PRS")
                ET.SubElement(father, 'code', code="NFTH")
                relationshipHolderFather = ET.SubElement(father, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderFather, 'id', extension="5")

                patientPerson.insert(patientPerson.index(NewMotherRelative),relative)
                patientPerson.remove(NewMotherRelative)


        # Maternal Great-Grandfather -> father
        elif((str)(relative.find('code').get('code'))== "MGGRFTH"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')

            # if the MGGRFTH's ID matches the original maternal grandmother father's id, he will be the new father
            if(id == MGRFTHFatherID):
                relative.find(".//code").set('code', "NFTH")
                relationshipHolder.find('id').set('extension', "3")

                mother = ET.SubElement(relationshipHolder, 'relative', classCode = "PRS")
                ET.SubElement(mother, 'code', code="NMTH")
                relationshipHolderMother = ET.SubElement(mother, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderMother, 'id', extension="6")
                father = ET.SubElement(relationshipHolder, 'relative', classCode = "PRS")
                ET.SubElement(father, 'code', code="NFTH")
                relationshipHolderFather = ET.SubElement(father, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderFather, 'id', extension="7")

                patientPerson.insert(patientPerson.index(NewFatherRelative),relative)
                patientPerson.remove(NewFatherRelative)

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
                # Check if the "NotAvailable" relative's mother is on the maternal side
                # If their mother falls in one of the first 7 ids, update accordingly
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    if motherID in globalVars.maternalSideIDS:
                        motherFound = True
                    if int(motherID) <= 7:
                        if int(motherID) == 1:
                            relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                        if int(motherID) == 2:
                            relationshipHolderNew.find('id').set('extension', str(OGmotherID))
                        if int(motherID) == 4:
                            relationshipHolderNew.find('id').set('extension', str(grandmotherId))   
                # Check if the "NotAvailable" relative's father is on the maternal side
                # If their father falls in one of the first 7 ids, update accordingly
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    if fatherID in globalVars.maternalSideIDS:
                        fatherFound = True
                    if int(fatherID) <= 7:
                        if int(fatherID) == 1:
                            relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                        if int(fatherID) == 3:
                            relationshipHolderNew.find('id').set('extension', str(OGfatherID))
                        if int(fatherID) == 5:
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

    # Finally, we will add the father relative, mother relative, grandfather relative (new patient's spouse),
    # and the original patient's relative that was created earlier
    patientPerson.append(grandmother)
    patientPerson.append(OGmother)
    patientPerson.append(OGfather)
    patientPerson.append(originalPatient)