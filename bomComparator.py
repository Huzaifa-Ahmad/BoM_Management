'''
    File name: bomComparator.py
    Author: Huzaifa Ahmad
    Date created: 12/07/2021
    Date last modified: 10/11/2021
    Python Version: 3.10.0
    ===============================
    |
    |
    |
    ===============================
'''
from llist import dllist, dllistnode
from typing import NoReturn
import csv
from comparisonFormatter import BoMUpdateFormatter


class BomComparator:
    """Constructor to create assign the old bom and new bom and turn into LL
    :param oldBoM: fileName of old BoM, string type
    :param newBoM: fileName of most recent BoM, string type
    """

    def __init__(self, oldBoM, newBoM, bomName):
        if isinstance(oldBoM, str) and isinstance(newBoM, str):
            oldBoM = self.parseTXTBoM(oldBoM)
            newBoM = self.parseTXTBoM(newBoM)

        self.oldBoM = oldBoM
        self.newBoM = newBoM
        self.bomName = bomName

        self.oldBoMdll = self.CreateLinkedListofMaterials(self.oldBoM)
        self.newBoMdll = self.CreateLinkedListofMaterials(self.newBoM)
        self.masterdll = dllist()

        self.comparingMaterialIndex = 0
        # name of the column of attribute of materials to compare
        # i.e. in this case we are comparing PNs in 2 lists, the BoM column name is 'PRT_NUMBER'
        self.compareMaterialLists()
        print(bomName + " BoMs Compared")

    # the LL this function creates are a Linked list of materials in a BoM
    # each Node is a row from the BoM

    def CreateLinkedListofMaterials(self, BoM):
        BoMll = dllist()
        BoMll.extend(BoM)
        return BoMll

    def compareMaterialLists(self):
        # creating a base list and a comparing list to differentiate the longer of the 2 (old & new) BoMs
        # the Nodes in the LL are strings representing component PNs (not DPNs) in the BoM
        self.baseMaterialsll = dllist()
        self.comparingMaterialsll = dllist()
        print('{}{}{}'.format("Comparing ", self.bomName, " BoMs"))

        # setting the longer bom as the base bom (compared to BoM is base, compared from BoM is comparing)
        if (self.newBoMdll.size) >= (self.oldBoMdll.size):
            self.baseMaterialsll.extend(self.newBoM)
            self.comparingMaterialsll.extend(self.oldBoM)
        else:
            self.baseMaterialsll.extend(self.oldBoM)
            self.comparingMaterialsll.extend(self.newBoM)

        self.buildMasterListR(self.comparingMaterialsll.first,
                              self.baseMaterialsll.first, None)

    """The recursive function to build the master list which has all components from old and new BoMs in order with status update
    :param materialInNewBoM: Node object consisting of the current material in the base BoM, DLListNode type
    :param materialToAppend: Node object consisting of the current material we are checking the status of in the comparing BoM , DLListNode type
    :param prevMaterialAppended: Node object consisting of the last material added to the master list from the comparing BoM, DLListNode type
    """

    def buildMasterListR(self, materialToAppend, materialInBaseBoM, prevMaterialAppended):
        materialExists = self.checkMaterialinBoM(materialToAppend)

        # base case at the end of the list and nothing else to be compared
        if (materialToAppend.next == None):
            return

        # case where item has been deleted so pointer to base BoM must be pushed ahead to account for lack of item that had been present in base BoM
        elif (materialToAppend.value[0] != materialInBaseBoM.value[0]) and materialExists:
            self.addMaterialToMaster(materialInBaseBoM, 'N')
            prevMaterialAppended = materialInBaseBoM.prev
            return self.buildMasterListR(materialToAppend, materialInBaseBoM.next, prevMaterialAppended)

        # case where item has not been changed and is at expected index after all prior deletions and additions to BoM

        elif (materialToAppend.value[0] == materialInBaseBoM.value[0]) and materialExists:
            self.addMaterialToMaster(materialToAppend, 'U')
            prevMaterialAppended = materialToAppend
            return self.buildMasterListR(materialToAppend.next, materialInBaseBoM.next, prevMaterialAppended)

        # case where item has been added so comparison pointer must be pushes ahead to match lack of material in base BoM
        else:
            self.addMaterialToMaster(materialToAppend, 'D')
            prevMaterialAppended = materialToAppend.next
            return self.buildMasterListR(materialToAppend.next, materialInBaseBoM, prevMaterialAppended)

    """Function to check if the material from the base comparing BoM still exists in the base BoM
    :param comparingMaterial: Node object of material we are checking presence for, DLListNode type
    :return bool, True if exists false if deleted
    """

    def checkMaterialinBoM(self, comparingMaterial):
        # iterating through base list looking for comparingMaterial
        for baseMaterial in self.baseMaterialsll.iternodes():
            if comparingMaterial.value[0] == baseMaterial.value[0]:
                return True
        return False

    def addMaterialToMaster(self, material, status):
        material.value.append(status)
        self.masterdll.append(material)
        self.comparingMaterialIndex += 1

    # takes a list of lists with bomData (no status of update in this list)
    def formatBoMUpdates(self, bomList):
        masterList = []
        for rowNode in self.masterdll.iternodes():
            masterList.append(rowNode.value)

        BoMUpdateFormatter(bomList, masterList, self.bomName)

    def parseTXTBoM(self, bomDir):
        bomData = []
        with open(bomDir, 'r') as bom:
            # skipping cadence logging info
            for _ in range(7):
                next(bom)

            # reading first line which is header data in the following convention
            # 0         1       2   3   4            5
            # Part Name Ref Des, Qty, Unit Price, Cost
            bom.readline()

            # parsing data line by line removing everything outside of data rows
            for cLine in csv.reader(bom, quotechar='"', delimiter=','):
                if cLine[0] != 'TOTAL':
                    bomData.append(cLine)
        return bomData


if __name__ == "__main__":
    oldBomDir = "Cadence BoMs/mpc_old.txt"  # change to old bom dir
    newBoMDir = "Cadence BoMs/mpc_new.txt"  # change to new bom dir
    bomName = "mpc"			                # change to output file name

    boMComparator = BomComparator(oldBomDir, newBoMDir, bomName)
    boMComparator.formatBoMUpdates(boMComparator.newBoM)
