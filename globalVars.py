def reset():
    global relativesArray
    relativesArray.clear()
    global relatives
    relatives.clear()
    global unavailableRelatives
    unavailableRelatives = []
    # Relative data paralell arrays
    global first_names
    first_names.clear()
    global last_names
    last_names.clear()
    global codes
    codes.clear()
    global genders
    genders.clear()
    global deceased
    deceased.clear()
    global ages
    ages.clear()
    global ids
    ids.clear()

    global originalGivenName 
    originalGivenName = ""
    global originalFamilyName
    originalFamilyName = ""
    global originalGender
    originalGender = ""
    global originalDOB
    originalDOB = ""
    global originalDeceased
    originalDeceased = ""
    global subjectOf2
    subjectOf2.clear()
    global subjectOf1
    subjectOf1.clear()

    global maternalSideIDS
    maternalSideIDS = ["1", "2"]
    global paternalSideIDS
    paternalSideIDS = ["1", "3"]

    global notAvailableIdsToAdd
    notAvailableIdsToAdd.clear()

    global notAvailableRelatives
    notAvailableRelatives.clear()

    global newPatientSubjectOf1
    newPatientSubjectOf1.clear()
    global newPatientSubjectOf2
    newPatientSubjectOf2.clear()

relativesArray  = []

relatives = []
unavailableRelatives = []
# Relative data paralell arrays
first_names = []
last_names = []
codes = []
genders = []
deceased = []
ages = []
ids = []

originalGivenName = ""
originalFamilyName = ""
originalGender = ""
originalDOB = ""
originalDeceased = ""
subjectOf2 = []
subjectOf1 = []

maternalSideIDS = ["1", "2"]
paternalSideIDS = ["1", "3"]

notAvailableIdsToAdd = []
notAvailableRelatives = []

newPatientSubjectOf1 = []
newPatientSubjectOf2 = []
