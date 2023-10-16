import globalVars
import xml.etree.ElementTree as ET

def rearrange(tree, patientPerson):
    currentId = 8
    for relative in globalVars.relativesArray:
        print(relative.find('code').get('code'))
        if((str)(relative.find('code').get('code'))== "PGRMTH"):
            relative.find(".//code").set('code', "NMTH")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', "2")

            relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
            ET.SubElement(relativeNew, 'code', code="NMTH")
            relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
            ET.SubElement(relationshipHolderNew, 'id', extension="4")

            relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
            ET.SubElement(relativeNew, 'code', code="NFTH")
            relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
            ET.SubElement(relationshipHolderNew, 'id', extension="5")

            patientPerson.append(relative)
        elif((str)(relative.find('code').get('code'))== "PGRFTH"):
            relative.find(".//code").set('code', "NFTH")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', "3")

            relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
            ET.SubElement(relativeNew, 'code', code="NMTH")
            relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
            ET.SubElement(relationshipHolderNew, 'id', extension="6")

            relativeNew = ET.SubElement(relationshipHolder, 'relative', classCode="PRS")
            ET.SubElement(relativeNew, 'code', code="NFTH")
            relationshipHolderNew = ET.SubElement(relativeNew, 'relationshipHolder', classCode="PSN", determinerCode="INSTANCE")
            ET.SubElement(relationshipHolderNew, 'id', extension="7")

            patientPerson.append(relative)
        elif((str)(relative.find(".//code").get('code')) == "NMTH"):
            relative.find(".//code").set('code', "NotAvailable")
            relationshipHolder = relative.find(".//relationshipHolder")
            relationshipHolder.find(".//id").set('extension', str(currentId))
            currentId += 1
            for x in relationshipHolder.findall(".//relative"):
                relationshipHolder.remove(x)

            patientPerson.append(relative)