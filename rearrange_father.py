import globalVars
# import xml.etree.ElementTree as ET
from lxml import etree as ET

def makeRelativeForOldPatient(originalPatient, motherId, currentId):
    if(globalVars.originalGender == "F"):
        ET.SubElement(originalPatient, 'code', code = "DAU")
    else:
        ET.SubElement(originalPatient, 'code', code = "SON")
    patientRelationshipHolder = ET.SubElement(originalPatient, 'relationshipHolder', classCode = "PSN", determinerCode="INSTANCE")
    ET.SubElement(patientRelationshipHolder, 'id', extension = str(currentId))
    originalPatientID = currentId
    name = ET.SubElement(patientRelationshipHolder, 'name')
    ET.SubElement(name, 'given').text = globalVars.originalGivenName
    ET.SubElement(name, 'family').text = globalVars.originalFamilyName
    ET.SubElement(patientRelationshipHolder, 'administrativeGenderCode', code = globalVars.originalGender)
    ET.SubElement(patientRelationshipHolder, 'birthTime', code = globalVars.originalDOB)
    ET.SubElement(patientRelationshipHolder, 'deceasedInd', code = globalVars.originalDeceased)
    NMTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    ET.SubElement(NMTHRelative, 'code', code = "NMTH")
    relationshipHolderNew = ET.SubElement(NMTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderNew, 'id', extension=str(motherId))
    NFTHRelative = ET.SubElement(patientRelationshipHolder, 'relative', classCode = "PRS")
    ET.SubElement(NFTHRelative, 'code', code = "NFTH")
    relationshipHolderNew = ET.SubElement(NFTHRelative, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
    ET.SubElement(relationshipHolderNew, 'id', extension="1")
    for data in globalVars.subjectOf1:
        originalPatient.append(data)

    for data in globalVars.subjectOf2:
        originalPatient.append(data)

    return originalPatientID

def rearrange(tree, patientPerson):
    currentId = 100

    for x in range(6):
        relative = globalVars.relativesArray[x]
        print(relative.find('code').get('code'))

        # PGRMTH becomes Mother
        if((str)(relative.find('code').get('code'))== "PGRMTH"):
            relative.find(".//code").set('code', "NMTH")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', "2")

            motherFound = False
            fatherFound = False
            PGRMTHMotherID = 0
            PGRMTHFatherID = 0
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

            if(motherFound != True):
                relativeNew = ET.Element('relative', classCode="PRS")
                ET.SubElement(relativeNew, 'code', code="NMTH")
                relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderNew, 'id', extension="4")
                if(fatherFound):
                    relationshipHolder.insert(relationshipHolder.index(fatherRelative), relativeNew)
                else:
                    relationshipHolder.append(relativeNew)
            if(fatherFound != True):
                relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
                ET.SubElement(relativeNew, 'code', code="NFTH")
                relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderNew, 'id', extension="5")

            patientPerson.append(relative)
        # PGRFTH becomes Father
        elif((str)(relative.find('code').get('code'))== "PGRFTH"):
            relative.find(".//code").set('code', "NFTH")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', "3")

            motherFound = False
            fatherFound = False
            PGRFTHMotherID = 0
            PGRFTHFatherID = 0
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

            if(motherFound != True):
                relativeNew = ET.Element('relative', classCode="PRS")
                ET.SubElement(relativeNew, 'code', code="NMTH")
                relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderNew, 'id', extension="6")
                if(fatherFound):
                    relationshipHolder.insert(relationshipHolder.index(fatherRelative), relativeNew)
                else:
                    relationshipHolder.append(relativeNew)
            if(fatherFound != True):
                relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
                ET.SubElement(relativeNew, 'code', code="NFTH")
                relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
                ET.SubElement(relationshipHolderNew, 'id', extension="7")

            patientPerson.append(relative)
        elif((str)(relative.find(".//code").get('code')) == "NMTH"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(currentId))
            motherId = currentId
            currentId += 1
            for x in relationshipHolder.findall(".//relative"):
                relationshipHolder.remove(x)

            mother = relative
        elif((str)(relative.find(".//code").get('code')) == "NFTH"):
            for subjectOf1Data in relative.findall('.//subjectOf1'):
                globalVars.newPatientSubjectOf1.append(subjectOf1Data)
            for subjectOf2Data in relative.findall('.//subjectOf2'):
                globalVars.newPatientSubjectOf1.append(subjectOf2Data)


    # Create a new relative element for the original patient
    # This is done here to ensure that the original patient's mother's ID has already been created
    originalPatient = ET.Element('relative', classCode = "PRS")
    originalPatientID = makeRelativeForOldPatient(originalPatient, motherId, currentId)
    currentId += 1

    # Create new grandparents. These will be updated if the original patient had Great Grandparents. Otherwise, they will stay blank.
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
        
    for x in range(6, len(globalVars.relativesArray)):
        relative = globalVars.relativesArray[x]
        print(relative.find('code').get('code'))

        if((str)(relative.find('code').get('code'))== "NSIS"):
            relative.find(".//code").set('code', "DAU")
            relationshipHolder = relative.find(".//relationshipHolder")
 
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(motherId))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "1") 
            patientPerson.append(relative)

        elif((str)(relative.find('code').get('code'))== "NBRO"):
            relative.find(".//code").set('code', "SON")
            relationshipHolder = relative.find(".//relationshipHolder")

            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', str(motherId))
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "1")
            patientPerson.append(relative)

        elif((str)(relative.find('code').get('code'))== "PAUNT"):
            relative.find(".//code").set('code', "NSIS")
            relationshipHolder = relative.find(".//relationshipHolder")
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "2")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "3")

            patientPerson.append(relative)
        elif((str)(relative.find('code').get('code'))== "PUNCLE"):
            relative.find(".//code").set('code', "NBRO")
            relationshipHolder = relative.find(".//relationshipHolder")
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "2")
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    relationshipHolderNew.find('id').set('extension', "3")

            patientPerson.append(relative)
        elif((str)(relative.find('code').get('code'))== "NIECE"):
            motherID = 0
            fatherID = 0
            motherFound = False
            fatherFound = False
            relative.find(".//code").set('code', "GRNDDAU")
            relationshipHolder = relative.find(".//relationshipHolder")
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    if motherID in globalVars.paternalSideIDS:
                        motherFound = True
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    if fatherID in globalVars.paternalSideIDS:
                        fatherFound = True

            if(motherFound or fatherFound):
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                patientPerson.append(relative)

        elif((str)(relative.find('code').get('code'))== "NEPHEW"):
            motherID = 0
            fatherID = 0
            motherFound = False
            fatherFound = False
            relative.find(".//code").set('code', "GRNDSON")
            relationshipHolder = relative.find(".//relationshipHolder")
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    if motherID in globalVars.paternalSideIDS:
                        motherFound = True
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    if fatherID in globalVars.paternalSideIDS:
                        fatherFound = True

            if(motherFound or fatherFound):
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                patientPerson.append(relative)

        elif((str)(relative.find('code').get('code'))== "PCOUSN"):
            relationshipHolder = relative.find(".//relationshipHolder")
            gender = relationshipHolder.find('administrativeGenderCode').get('code')
            if(gender == "F"):
                relative.find(".//code").set('code', "NIECE")
            else:
                relative.find(".//code").set('code', "NEPHEW")

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
        elif((str)(relative.find('code').get('code'))== "DAU"):
            relative.find(".//code").set('code', "GRNDDAU")
            relationshipHolder = relative.find(".//relationshipHolder")
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
        elif((str)(relative.find('code').get('code'))== "SON"):
            relative.find(".//code").set('code', "GRNDSON")
            relationshipHolder = relative.find(".//relationshipHolder")
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
        elif((str)(relative.find('code').get('code'))== "PGGRMTH"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')
            if(id == PGRMTHMotherID):
                relative.find(".//code").set('code', "MGRMTH")
                relationshipHolder.find('id').set('extension', "4")
                patientPerson.insert(patientPerson.index(MGRMTHRelative),relative)
                patientPerson.remove(MGRMTHRelative)
            elif(id == PGRFTHMotherID):
                relative.find(".//code").set('code', "PGRMTH")
                relationshipHolder.find('id').set('extension', "6")
                patientPerson.insert(patientPerson.index(PGRMTHRelative),relative)
                patientPerson.remove(PGRMTHRelative)
        elif((str)(relative.find('code').get('code'))== "MGGRFTH"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')
            if(id == PGRMTHFatherID):
                relative.find(".//code").set('code', "MGRFTH")
                relationshipHolder.find('id').set('extension', "5")
                patientPerson.insert(patientPerson.index(MGRFTHRelative),relative)
                patientPerson.remove(MGRFTHRelative)
            elif(id == PGRFTHFatherID):
                relative.find(".//code").set('code', "PGRFTH")
                relationshipHolder.find('id').set('extension', "7")
                patientPerson.insert(patientPerson.index(PGRFTHRelative),relative)
                patientPerson.remove(PGRFTHRelative)
        elif((str)(relative.find('code').get('code'))== "NotAvailable"):
            globalVars.notAvailableRelatives.append(relative)
            motherFound = False
            fatherFound = False
            motherID = 0
            fatherID = 0
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')
            for x in relationshipHolder.findall(".//relative"):
                if(x.find('code').get('code') == "NMTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    motherID = relationshipHolderNew.find('id').get('extension')
                    if motherID in globalVars.paternalSideIDS:
                        motherFound = True
                    if int(motherID) <= 7:
                        if int(motherID) == 1:
                            relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                        if int(motherID) == 2:
                            relationshipHolderNew.find('id').set('extension', str(motherID))
                        if int(motherID) == 6:
                            relationshipHolderNew.find('id').set('extension', "2")   
                elif(x.find('code').get('code') == "NFTH"):
                    relationshipHolderNew = x.find('relationshipHolder')
                    fatherID = relationshipHolderNew.find('id').get('extension')
                    if fatherID in globalVars.paternalSideIDS:
                        fatherFound = True
                    if int(fatherID) <= 7:
                        if int(fatherID) == 1:
                            relationshipHolderNew.find('id').set('extension', str(originalPatientID))
                        if int(fatherID) == 3:
                            relationshipHolderNew.find('id').set('extension', "1")
                        if int(fatherID) == 7:
                            relationshipHolderNew.find('id').set('extension', "3") 
            
            if(motherFound or fatherFound):
                if(fatherFound and int(motherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(motherID)
                if(motherFound and int(fatherID) != 0):
                    globalVars.notAvailableIdsToAdd.append(fatherID)
                globalVars.notAvailableIdsToAdd.append(id)


    for x in range(0, len(globalVars.notAvailableRelatives)):
        relative = globalVars.notAvailableRelatives[x]
        print(relative.find('code').get('code'))
        if((str)(relative.find('code').get('code'))== "NotAvailable"):
            relationshipHolder = relative.find(".//relationshipHolder")
            id = relationshipHolder.find('id').get('extension')
            if(id in globalVars.notAvailableIdsToAdd):
                patientPerson.append(relative)

    patientPerson.append(mother)
    patientPerson.append(originalPatient)