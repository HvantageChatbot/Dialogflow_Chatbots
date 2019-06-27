# Author: Raghav Mundhra, Roochin Dwivedi, Chayan Bansal
# Version : 4.1

import json
import os
from flask import Flask
from flask import request
from flask import make_response
from urllib.request import urlopen
from collections import defaultdict
from Menu import Menu  
from Items import Items 
from Category import Category
import requests

app = Flask(__name__)

# Global variables for paymentApi format and session using email as keys and value as respective carts
################################
global email_dict,paymentPOST ##
################################
email_dict = defaultdict(list)
paymentPOST = defaultdict(dict)
menu = Menu()

@app.route('/webhook',methods = ['POST'])
def webhook(): 
    # Menu class global instance
    global menu
    req = request.get_json(silent=True,force=True)
    # returns a dictionary based on individual intent action
    res = makeWebhookResult(req,menu)
    res = json.dumps(res,indent = 4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def fetchMail(req):
    '''
    Extracts email id from the given request json data.
    \nInput: Request JSON.
    \nReturns Email Id string
    '''
    if req['queryResult']['outputContexts'][0]['parameters']['email']:
        email_id = req['queryResult']['outputContexts'][0]['parameters']['email']
    else:
        email_id = req['queryResult']['outputContexts'][1]['parameters']['email']
    return email_id

def check_email(email):

    '''
    \nAdds email id to the global dictionary.
    \nShould take the following as input
    email = req['queryResult']['outputContexts'][0]['parameters']['email']
    '''
    if email not in email_dict:
        email_dict[email] = None

def makeSpeech(speech):
    return {'textToSpeech': speech,'displayText': speech,'fulfillmentText': speech}

def makeWebhookResult(req,menu):
    '''
    Returns a dictionary based on individual intent action
    '''
    # Deal with the intent - showMenu
    if req['queryResult']['action'] == 'showMenuAction':
        speech = "The details you asked are : \n\n " + "\n".join([str(i) for i in list(menu.extractMenu())])
        return makeSpeech(speech)
     # Deal with the intent - showCategory
    elif req['queryResult']['action'] == 'expandMenuAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        category = parameters.get('categoryEntity')
        cat = Category()
        cat.extractCatergoryId(category)
        speech = "The details you asked are : \n\n " + "\n".join([str(i) for i in list(cat.getdata())])
        return makeSpeech(speech)
    # Deal with the intent - exploreItem
    elif req['queryResult']['action'] == 'exploreItemAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        item = parameters.get('items')
        it = Items()
        plateDetails = it.exploreItem(item)
        speech = "Price for " + str(item) + "\n\n" + "for half plate: " + plateDetails[0] +  "\nfull plate: " + plateDetails[1]
        return makeSpeech(speech)
    # Deal with the intent - addThisToCart 
    # Used when user is exploring a specific item and then says to add the item which is being explored to the cart.
    elif req['queryResult']['action'] == 'addThisToCartAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        quantity = parameters.get('quantity')
        platesize = parameters.get("plateSize")
        if quantity and platesize:
            item_name = req['queryResult']['outputContexts'][0]['parameters']['items']
            email_id = fetchMail(req)
            it1 = Items()
            price_both = it1.exploreItem(item_name) # item plate size and menuID
            if platesize == "full":
                price = price_both[1]
            elif platesize == "half" and price_both[0] != "Not Available":
                price = price_both[0]
            else:
                price = price_both[1]
                platesize = "full (Half-not available)"
            temp_dict = {'item_name':item_name,'quantity':quantity,'price':int(quantity)*int(price[1:]),'plate_size':platesize}
            email_dict[email_id].append(temp_dict)
            paymentPOST[email_id]['cart'] = [{'name':item_name,'id':price_both[2],'quantity':int(quantity),'type':"ANY",'price':int(price[1:])}]
            speech = "Cart Updated Successfully !"
            return makeSpeech(speech)

    # Deal with the intent - clearCart
    elif req['queryResult']['action'] == 'clearCartAction':
        email_id = fetchMail(req)
        if email_id in email_dict:
            del email_dict[email_id]
    # Deal with the intent - addItemToCart
    # Used when user says add @ITEM_NAME to cart directly.
    elif req['queryResult']['action'] == 'addItemToCartAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        quantity = parameters.get('quantity')
        platesize = parameters.get("plateSize")
        if quantity and platesize:
            item_name = req['queryResult']['outputContexts'][0]['parameters']['items']
            email_id = fetchMail(req)
            it2 = Items()
            price_both = it2.exploreItem(item_name)
            if platesize == "full":
                price = price_both[1]
            elif platesize == "half" and price_both[0] != "Not Available":
                price = price_both[0]
            else:
                price = price_both[1]
                platesize = "full (Half-not available)"
            # Cart updation to show user
            temp_dict = {'item_name':item_name,'quantity':quantity,'price':int(quantity)*int(price[1:]),'plate_size':platesize}
            email_dict[email_id].append(temp_dict)
            paymentPOST[email_id]['cart'] = [{'name':item_name,'id':price_both[2],'quantity':int(quantity),'type':"ANY",'price':int(price[1:])}]
            speech = "Cart Updated Successfully !"
            return makeSpeech(speech)     

    # Deal with the intent - placeOrder
    elif req['queryResult']['action'] == 'placeOrderAction':
        result = req['queryResult']
        parameters = result.get('parameters')
        name = parameters.get("name")
        mobile  = parameters.get("mobile")
        address = parameters.get("address")
        landmark = parameters.get('landmark')
        city = parameters.get('city')
        pincode = parameters.get('pincode')
        if name and mobile and address and city and pincode:
            email_id = fetchMail(req)
            # Updating Payment Api format for POST request
            paymentPOST[email_id]['customer'] = [{'name':name,
                                                    'number':mobile,
                                                    'email':email_id,
                                                    'address':address,
                                                    'landmark':landmark,
                                                    'city':city,
                                                    'pincode':int(pincode)}]
            makeSpeech("Redirecting to payment gateway...")
            # Post request to payment API
            linkRequest = requests.post(url = menu.paymentAPI, data = json.dumps(paymentPOST[email_id])) 
            return makeSpeech("This is your payment link click on the link and complete your payment. Thankyou for ordering !\n\n" + str(linkRequest.text))

    # Deal with the intent - shoeCart
    elif req['queryResult']['action'] == 'showCartAction':
        result = req['queryResult']
        email_id = fetchMail(req)
        no = 1
        speech = ""
        for i in email_dict[email_id]:
            speech += "Item: " + str(no) + "\n"
            for k in i:
                speech += str(k)+"-"+str(i[k]) + "\n"
            no += 1
        return makeSpeech(speech)

if __name__ == "__main__":
    port = int(os.getenv('PORT',80))    
    app.run(debug=True,port = port,host = '0.0.0.0')



