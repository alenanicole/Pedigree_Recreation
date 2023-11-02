import globalVars
from lxml import etree as ET

# Create a new relative element to hold the original patient's information.
# Since this function correlates to the rearrange_son section, the original
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
        ET.SubElement(GRMTHRelative, 'code', code = "MGRMTH")
        relationshipHolderNew = ET.SubElement(GRMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="4")     # give the old patient the correct grandmother
    else:
        ET.SubElement(GRMTHRelative, 'code', code = "PGRMTH")
        relationshipHolderNew = ET.SubElement(GRMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="6")     # give the old patient the correct grandmother
    
    # Make the oldPatient's father a grandfather
    # Paternal/Maternal will be determined by looking at the originalPatient's gender
    GRFTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    
    if(originalPatientID == 2):
        ET.SubElement(GRFTHRelative, 'code', code = "MGRFTH")
        relationshipHolderNew = ET.SubElement(GRFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
        ET.SubElement(relationshipHolderNew, 'id', extension="5") # give the old patient the correct grandfather
    else:
        ET.SubElement(GRFTHRelative, 'code', code = "PGRFTH")
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
    currentId = 100 # Any new relatives to be added will start with the ID of 100
    # variables to find the spouse's ID
    spouseIDfound = False
    spouseID = 1

    # Create a new relative element for the original patient
    originalPatient = ET.Element('relative', classCode = "PRS")
    originalPatientID = makeRelativeForOldPatient(originalPatient)

    # The first 6 members of the family will be dealt with first.
    # This includes the mother, father, maternal grandmother, and maternal grandfather
    # The paternal grandmother and paternal grandfather are also included in these 6 relatives
    for relative in globalVars.relativesArray:
        # Brother -> Uncle (Paternal or Maternal TBD)
        if((str)(relative.find('code').get('code'))== "NBRO"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MUNCLE")
                relationshipHolder = relative.find(".//relationshipHolder")
            else:
                relative.find(".//code").set('code', "PUNCLE")
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

        # Sister -> Aunt (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NSIS"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MAUNT")
                relationshipHolder = relative.find(".//relationshipHolder")
            else:
                relative.find(".//code").set('code', "PAUNT")
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

        # Daughter -> Sister
        elif((str)(relative.find('code').get('code'))== "DAU"):
            relative.find(".//code").set('code', "NSIS")
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

        # Son -> Brother / Patient
        elif((str)(relative.find('code').get('code'))== "SON"):
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
                relative.find(".//code").set('code', "NBRO") # update to sister if not the new patient

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

        ## The grandparents will be the same side of the family 
        ## All of them either Paternal or Maternal NO COMBINATION
        # Mother -> Grandmother (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NMTH"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MGRMTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', "4") # update from mother id to maternal grandma id
            else:
                relative.find(".//code").set('code', "PGRMTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', "6") # update from mother id to paternal grandma id

            # Fix the parent ids from their current #4-7 to new currentIDs
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"): # update NMTH to the correct great grandmotherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
                    else: 
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
                elif(x.find('code').get('code') == "NFTH"): # update NFTH to the correct great grandfatherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
                    else: 
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
            patientPerson.append(relative)

        # Father -> Grandfather (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NFTH"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MGRFTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', "5") # update from father id to maternal grandpa id
            else:
                relative.find(".//code").set('code', "PGRFTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', "7") # update from father id to paternal grandpa id

            # Fix the parent ids from their current #4-7 to new currentIDs
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"): # update NMTH to the correct great grandmotherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
                    else: 
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
                elif(x.find('code').get('code') == "NFTH"): # update NFTH to the correct great grandfatherID
                    relationshipHolderNew = x.find('relationshipHolder')
                    if(originalPatientID == 2):
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
                    else: 
                        relationshipHolderNew.find('id').set('extension', str(currentId))
                        currentId += 1
            patientPerson.append(relative)

        # need the spouse id from the Old patient to change from "NotAvailable"
        # to NFTH, then create the side of grandparents that are missing
        elif((str)(relative.find('code').get('code'))== "NotAvailable"):
            if(spouseIDfound & spouseID != 1):
                if(originalPatientID == 2): # if the patient is female then make him dad
                    relative.find(".//code").set('code', "NFTH")
                    relationshipHolder = relative.find(".//relationshipHolder")
                    relationshipHolder.find(".//id").set('extension', "3") # update from spouseID to 3
                else: # the patient is male and make her the mom
                    relative.find(".//code").set('code', "NMTH")
                    relationshipHolder = relative.find(".//relationshipHolder")
                    relationshipHolder.find(".//id").set('extension', "2") # update from spouseID to 2

                spouseFatherFound = False
                spouseMotherFound = False
                FatherID = 0
                MotherID = 0

                # update spouse parent codes if they exist
                for x in relationshipHolder.findall(".//relative"):
                    if(x.find('code').get('code') == "NMTH"): # update NMTH to the correct grandmotherID
                        relationshipHolderNew = x.find('relationshipHolder')
                        MotherID = relationshipHolderNew.find('id').get('extension')
                        if(originalPatientID == 2): # if old patient was mother, spouse parents are paternal
                            relationshipHolderNew.find('id').set('extension', "6")
                        else: # if old patient was father, spouse parents are maternal
                            relationshipHolderNew.find('id').set('extension', "4")
                        spouseMotherFound = True
                    elif(x.find('code').get('code') == "NFTH"): # update NFTH to the correct great grandfatherID
                        fatherRelative = x
                        relationshipHolderNew = x.find('relationshipHolder')
                        FotherID = relationshipHolderNew.find('id').get('extension')
                        if(originalPatientID == 2): # if old patient was mother, spouse parents are paternal
                            relationshipHolderNew.find('id').set('extension', "7")
                        else: # if old patient was father, spouse parents are maternal
                            relationshipHolderNew.find('id').set('extension', "5")
                        spouseFatherFound = True
                
                # either the paternal or maternal grandparents are missing and they must be present
                # here they will be acknowledged as the correct grandparents to one of the new patient's parents

                # If they do not currently have a mother, add one
                if(spouseMotherFound != True):
                    relativeNew = ET.Element('relative', classCode="PRS")
                    ET.SubElement(relativeNew, 'code', code="NMTH")
                    relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                    if(originalPatientID == 2): # make sure spouse parent ids are correct
                        ET.SubElement(relationshipHolderNew, 'id', extension="6")
                    else:
                        ET.SubElement(relationshipHolderNew, 'id', extension="4")
                    if(spouseFatherFound):
                        relationshipHolder.insert(relationshipHolder.index(fatherRelative), relativeNew)
                    else:
                        relationshipHolder.append(relativeNew)
                # If they do not currently have a father, add one
                if(spouseFatherFound != True):
                    relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
                    ET.SubElement(relativeNew, 'code', code="NFTH")
                    relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                    if(originalPatientID == 2): # make sure spouse parent ids are correct
                        ET.SubElement(relationshipHolderNew, 'id', extension="7")
                    else:
                        ET.SubElement(relationshipHolderNew, 'id', extension="5")
            
            patientPerson.append(relative)

        ## The great-grandparents will be the same side of the family 
        ## All of them either Paternal or Maternal NO COMBINATION
        # Paternal Grandfather -> Great-Grandfather (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "PGRFTH"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MGGRFTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from paternal grandpa id to maternal great grandpa id
                currentId += 1
            else:
                relative.find(".//code").set('code', "PGGRFTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from paternal grandpa id to paternal great grandpa id
                currentId += 1

            patientPerson.append(relative)

        # Paternal Grandmother -> Great-Grandmother (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "PGRMTH"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MGGRMTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from paternal grandma id to maternal great grandma id
                currentId += 1
            else:
                relative.find(".//code").set('code', "PGGRMTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from paternal grandma id to paternal great grandma id
                currentId += 1

            patientPerson.append(relative)

        # Maternal Grandfather -> Great-Grandfather (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "MGRFTH"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MGGRFTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from maternal grandpa id to maternal great grandpa id
                currentId += 1
            else:
                relative.find(".//code").set('code', "PGGRFTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from maternal grandpa id to paternal great grandpa id
                currentId += 1

            patientPerson.append(relative)

        # Maternal Grandmother -> Great-Grandmother (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "MGRMTH"):
            if(originalPatientID == 2): # determine wether paternal or maternal
                relative.find(".//code").set('code', "MGGRMTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from maternal grandma id to maternal great grandma id
                currentId += 1
            else:
                relative.find(".//code").set('code', "PGGRMTH")
                relationshipHolder = relative.find(".//relationshipHolder")
                relationshipHolder.find(".//id").set('extension', str(currentId)) # update from maternal grandma id to paternal great grandma id
                currentId += 1

            patientPerson.append(relative)

        # Paternal Aunt -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "PAUNT"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            patientPerson.append(relative)

        # Paternal Uncle -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "PUNCLE"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            patientPerson.append(relative)

        # Maternal Aunt -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "MAUNT"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            patientPerson.append(relative)

        # Maternal Uncle -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "MUNCLE"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable"code
            patientPerson.append(relative)

        # Grandchildren -> (niece/nephew) OR (son/daughter)
        # if the daughter is the new patient then change ID
        elif((str)(relative.find('code').get('code'))== "GRNDDAU"):
            #change to niece NOW and correct later if mother is new patient
            relative.find(".//code").set('code', "NIECE")
            relationshipHolder = relative.find(".//relationshipHolder")
            
            #it is rearrange_daughter so if grandchild mother is the new patient, change ID
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    if(motherID == BeforePatientID): # change id of mother to patientID if her id matches BeforePatientID
                        relationshipHolderNew.find('id').set('extension', "1")
                        # if the mother is the patient then switch from NIECE to DAU
                        relative.find(".//code").set('code', "DAU")
            
            patientPerson.append(relative)

        elif((str)(relative.find('code').get('code'))== "GRNDSON"):
            #change to nephew NOW and correct later if mother is new patient
            relative.find(".//code").set('code', "NEPHEW")
            relationshipHolder = relative.find(".//relationshipHolder")

            #it is rearrange_daughter so if grandchild mother is the new patient, change ID
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    if(motherID == BeforePatientID): # change id of mother to patientID if her id matches BeforePatientID
                        relationshipHolderNew.find('id').set('extension', "1")
                        # if the mother is the patient then switch from NEPHEW to SON
                        relative.find(".//code").set('code', "SON")
            
            patientPerson.append(relative)

        # Niece -> Cousin (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NIECE"):
            if(originalPatientID == 2):
                relative.find(".//code").set('code', "MCOUSN") # Update to Maternal cousin code
            else:
                relative.find(".//code").set('code', "PCOUSN") # Update to Paternal cousin code
            patientPerson.append(relative)

        # Nephew -> Cousin (Paternal or Maternal TBD)
        elif((str)(relative.find('code').get('code'))== "NEPHEW"):
            if(originalPatientID == 2):
                relative.find(".//code").set('code', "MCOUSN") # Update to Maternal cousin code
            else:
                relative.find(".//code").set('code', "PCOUSN") # Update to Paternal cousin code
            patientPerson.append(relative)

        # Paternal Cousin -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "PCOUSN"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            patientPerson.append(relative)

        # Maternal Cousin -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "MCOUSN"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            patientPerson.append(relative)

        # Cousin -> "NotAvailable"
        elif((str)(relative.find('code').get('code'))== "COUSN"):
            relative.find(".//code").set('code', "NotAvailable") # Update to "NotAvailable" code
            patientPerson.append(relative)

        else:
            patientPerson.append(relative)

    # Create new grandparents. Only the Paternal or Maternal Grandparents set will get added depending on the og Patient's gender
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

    # add the old patient as the sibling they now are to the new patient
    if(originalPatientID == 2):
        patientPerson.append(PGRFTHRelative)
        patientPerson.append(PGRMTHRelative)
    else:
        patientPerson.append(MGRFTHRelative)
        patientPerson.append(MGRMTHRelative)
    patientPerson.append(originalPatient)