import json
from urllib.request import urlopen

class Menu:
    '''
    Main menu class having all the api links and loaded json data in the variables.
    \nAlso contains the cart list.
    \nContains one method Menu.extractMenu() which return list of menu items.
    '''
    def __init__(self):
        # menu api
        self.urlMenu = "http://www.mealgaadi.in/Meal_API/products_api.php?query=product_category"
        self.jsonData = json.load(urlopen(self.urlMenu))
        # category api
        self.urlCategory = "http://www.mealgaadi.in/Meal_API/products_api.php?query=product_menus_all"
        # payment api
        self.paymentAPI = " https://www.mealgaadi.in/Meal_API/order_api.php?query=orderPaymentRequest"
        self.categoryId = ""
        self.subCatData = json.load(urlopen(self.urlCategory))
        # cart variable
        self.cart = []
        self.lastComboEntry = 0
        
    def extractMenu(self):
        menuItems = []
        for menuObject in self.jsonData:
            if menuObject == 'result':
                for block in self.jsonData[menuObject]:
                    for property in block:
                        if property == "name":
                            menuItems.append(" ".join(block[property].split()))
        return menuItems
    
