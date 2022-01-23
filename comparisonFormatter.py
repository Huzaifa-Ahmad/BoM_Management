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
import os
import xlsxwriter
from xlsxwriter import workbook


class BoMUpdateFormatter:
    def __init__(self, bomDataList, bomStatusList, bomName):
        self.bomDataList = bomDataList
        self.bomStatusList = bomStatusList
        self.bomName = bomName
        self.workbookDir = "Gen Bom\\" + self.bomName + '_BOM.xlsx'
        if os.path.exists(self.workbookDir):
            os.remove(self.workbookDir)
            print("Previous " + self.bomName + " Comparison XLSX Deleted")
        else:
            print("The file does not exist")

        self.generateXlsx()
        print(self.bomName + " Comparison XLSX Created!\n")

    def generateXlsx(self):
        # create a new workbook that will have 2 sheets one with this weeks bom one with the updates marked up
        self.workbook = xlsxwriter.Workbook(self.workbookDir)

        # creating 2 sheets in the workbook
        bomDataSheet = self.workbook.add_worksheet(self.bomName + "_BOM")
        bomStatusSheet = self.workbook.add_worksheet(
            self.bomName + "_BOM_MARKED_UP")

        self.createStatusFormats()

        # writing the 2 lists passed to the class to the workbook sheets
        self.writeListToXlsx(self.bomDataList, bomDataSheet)
        self.writeListToXlsx(self.bomStatusList, bomStatusSheet)
        self.workbook.close()

    def writeListToXlsx(self, bomList, worksheet):
        if (len(bomList[0]) == 10):
            for rowNum, material in enumerate(bomList):
                worksheet.write_row(rowNum, 0, material,
                                    self.assignFormat(material[9]))
        else:
            for rowNum, material in enumerate(bomList):
                worksheet.write_row(rowNum, 0, material)

    def createStatusFormats(self):
        newMaterialProps = {
            'pattern': 1,
            'bg_color': 'green',
        }

        delMaterialProps = {
            'pattern': 1,
            'bg_color': 'red',
        }
        self.newMaterialFormat = self.workbook.add_format(newMaterialProps)
        self.delMaterialFormat = self.workbook.add_format(delMaterialProps)

    def assignFormat(self, status):
        match status:
            case 'U':
                return None
            case 'N':
                return self.newMaterialFormat
            case 'D':
                return self.delMaterialFormat
