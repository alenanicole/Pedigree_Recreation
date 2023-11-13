import globalVars
from lxml import etree as ET

#### MAKE relative for old patient
# Create a new relative element to hold the original patient's information.
# Since this function correlates to the rearrange_sister section, the original
# patient will become a brother or sister.
def makeRelativeForOldPatient(originalPatient, currentId):
    # Determine if the old patient will be a brother or sister based on gender
    if(globalVars.originalGender == "F"):
        ET.SubElement(originalPatient, 'code', code = "NSIS")
    else:
        ET.SubElement(originalPatient, 'code', code = "NBRO")
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
    ET.SubElement(relationshipHolderNew, 'id', extension="2")     # give the old patient the same mother as new
    NFTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    ET.SubElement(NFTHRelative, 'code', code = "NFTH")
    relationshipHolderNew = ET.SubElement(NFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderNew, 'id', extension="3") # give the old patient the same father as new

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
    currentMaxId = (int)(max(globalVars.ids))
    # Any new relatives to be added will start with lowest unused id
    currentId = (int)(globalVars.currentMaxId) + 1

    # Create a new relative element for the original patient
    originalPatient = ET.Element('relative', classCode = "PRS")
    originalPatientID = makeRelativeForOldPatient(originalPatient, currentId)
    currentId += 1

    # The first 6 members of the family will be dealt with first.
    # This includes the mother, father, maternal grandmother, and maternal grandfather
    # The paternal grandmother and paternal grandfather are also included in these 6 relatives
    for relative in globalVars.relativesArray:
        # Brother -> Brother (they will not change)
        if((str)(relative.find('code').get('code'))== "NBRO"):
            patientPerson.append(relative)

        # Sister -> Sister / Patient
        elif((str)(relative.find('code').get('code'))== "NSIS"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find("id").get("extension")
            # If they are the patient, we will collect their subjectOf1 and subjectOf2 data 
            # Then we will move on to the next patient as they do not need to be added as a relative
            if((str)(id) == (str)(BeforePatientID)):
                # Since the new patient is the sister, we must collect some data about her that will be
                # added later in main.py after rearrangment
                for subjectOf1Data in relative.findall('.//subjectOf1'):
                    globalVars.newPatientSubjectOf1.append(subjectOf1Data)
                for subjectOf2Data in relative.findall('.//subjectOf2'):
                    globalVars.newPatientSubjectOf1.append(subjectOf2Data)
                continue

            patientPerson.append(relative)

        # niece -> Daughter if motherID matches newPatientID
        elif((str)(relative.find('code').get('code'))== "NIECE"):
            relationshipHolder = relative.find(".//relationshipHolder")

            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    MotherID = relationshipHolderNew.find('id').get('extension')
                    # check if Niece's mother is our new patient
                    if(MotherID == BeforePatientID):
                        relative.find(".//code").set('code', "DAU") # Update to daughter code
                        relationshipHolderNew.find('id').set('extension', "1")

            patientPerson.append(relative)

        # Nephew -> Son if motherID matches newPatientID
        elif((str)(relative.find('code').get('code'))== "NEPHEW"):
            relationshipHolder = relative.find(".//relationshipHolder")

            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    MotherID = relationshipHolderNew.find('id').get('extension')
                    # check if Nephew's mother is our new patient
                    if(MotherID == BeforePatientID):
                        relative.find(".//code").set('code', "SON") # Update to son code
                        relationshipHolderNew.find('id').set('extension', "1")

            patientPerson.append(relative)

        # Daughter -> Niece
        elif((str)(relative.find('code').get('code'))== "DAU"):
            relative.find(".//code").set('code', "NIECE") # Update to Niece code
            relationshipHolder = relative.find(".//relationshipHolder")

            # family id extensions fixed to the old patient id created if necessary 
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                  # Add check for old patient
                    if(motherID == '1'):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                  # Add check for old patient
                    if(fatherID == '1'):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))

            patientPerson.append(relative)

        # Son -> Nephew
        elif((str)(relative.find('code').get('code'))== "SON"):
            relative.find(".//code").set('code', "NEPHEW") # Update to Nephew code
            relationshipHolder = relative.find(".//relationshipHolder")

            # family id extensions fixed to the old patient id created if necessary 
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                  # Add check for old patient
                    if(motherID == '1'):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                  # Add check for old patient
                    if(fatherID == '1'):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))

            patientPerson.append(relative)

        # Niece and nephew children are "NotAvailable" 
        # Grand(son/daughter) -> "Not Available"
        # The ids won't be changing
        elif((str)(relative.find('code').get('code'))== "GRNDDAU"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            patientPerson.append(relative)

        elif((str)(relative.find('code').get('code'))== "GRNDSON"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            patientPerson.append(relative)

        # Not available change ids
        #check parents. if parent is old or new patient then update their ID
        elif((str)(relative.find('code').get('code'))== "NotAvailable"):
            relationshipHolder = relative.find(".//relationshipHolder")

            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                  # Add check for old patient
                    if(motherID == '1'):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                 # Add check for new patient
                    if(motherID == BeforePatientID):
                        relationshipHolderNew.find('id').set('extension', "1")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                  # Add check for old patient
                    if(fatherID == '1'):
                        relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                 # Add check for new patient
                    if(fatherID == BeforePatientID):
                        relationshipHolderNew.find('id').set('extension', "1")

            patientPerson.append(relative)

        else:
            patientPerson.append(relative)

    # add the old patient as the sibling they now are to the new patient
    patientPerson.append(originalPatient)