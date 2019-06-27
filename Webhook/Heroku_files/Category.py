import json
from urllib.request import urlopen
from Menu import Menu

class Category(Menu):
    '''
    Category class is inheriting Menu class.
    Contains two methods i.e., Category.extractCategoryId(category) and Category.getdata().
    Category.extractCategoryId(category) takes argument the category for which,
    we need an ID and save it to self.categoryId.
    Category.getdata() returns list of all the data having self.categoryId == id.
    Category.getdata() returns a list of the category example list of snacks...
    '''

    def extractCatergoryId(self,category):
        for menuObject in self.jsonData:
            if menuObject == 'result':
                for block in self.jsonData[menuObject]:
                    for property in block:
                        if property == "name" and  (block[property].strip() == category):
                            self.categoryId = block['category_Id']

    def getdata(self):
        comboNumber = self.lastComboEntry
        subCatItem = []
        for menuObject in self.subCatData:
            if menuObject == 'result':
                for block in self.subCatData[menuObject]:
                    for property in block:
                        if property == "name" and block['category_Id'] == self.categoryId:
                            if "+" in block[property]:
                                comboNumber += 1
                                subCatItem.append("Combo :" + str(comboNumber) + " (" + block[property].replace("+","and") + " )" )
                            else:
                                subCatItem.append(block[property])
        self.lastComboEntry = comboNumber
        return subCatItem
    
