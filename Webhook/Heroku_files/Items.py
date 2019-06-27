import json
from urllib.request import urlopen
from Menu import Menu
import re

class Items(Menu):
    ''' 
    Items class is inheriting Menu class.
    Items class has one method i.e., Items.exploreItem(item).
    Items.exploreItem(item) takes one argument "item" which is the item name that we input on dialogflow.
    Items.exploreItem(item) return a list having list[0] = halfplate,list[1] = fullplate, list[2] = menuID.
    Items.formateApiData(String) formates data from API and removes brackets because dialogflow entity does not support brackets. 
    '''

    def formateApiData(self,S):
        S = re.sub('[0-9()]',"", S)
        return S.strip()

    def exploreItem(self,item):
        # Any item can be served based on size.Either Full or Half or both
        halfPlate = "Not Available"
        fullPlate = "Not Available"
        menuId = ""
        """ self.subCatData is defined at the constructor of Menu class,
         this variable contains the json file from the api call.
         API - "http://www.mealgaadi.in/Meal_API/products_api.php?query=product_menus_all"""
        for menuObject in self.subCatData:
            if menuObject == 'result':
                for block in self.subCatData[menuObject]:
                    for property in block:
                        if property == "name" and self.formateApiData(block[property]) == item:
                            # we also grab menu ID of specific item for payment Api
                            menuId = block['menu_Id']
                            if block['Half']:
                                # u"\u20B9" is printing rupee symbol
                                halfPlate =  u"\u20B9" + block['Half']
                                fullPlate =  u"\u20B9" + block['Full']
                            else:
                                fullPlate =  u"\u20B9" + block['single_Price']
        return [halfPlate,fullPlate,menuId]
    