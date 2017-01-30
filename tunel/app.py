from flask import (
    Flask, 
    render_template, 
    request, 
    jsonify
)

from database import (
    get_cache
)

from numpy.random import choice
from datetime import datetime
import requests
import numpy
import pandas
import json
import re
import os

# SERVER CONFIGURATION ##############################################
class TunelServer(Flask):

    def __init__(self, *args, **kwargs):
        super(TunelServer, self).__init__(*args, **kwargs)

        # load data on start of application
        self.cache = get_cache()

    def read_auth(self,auth_file):
        '''read_auth returns a single line (first) in a text file
        :param auth_file: full path to file to read
        '''
        filey = open(auth_file,"r")
        text = filey.readlines()[0].strip("\n")
        filey.close()
        return text

# Start application
app = TunelServer(__name__)
#app.transactions = get_transactions()          
#app.accounts = get_accounts()


# Views ##############################################################################################

@app.route("/")
def index():
    '''index shows the user a main view of things to do'''
    message_options = ["Don't type it, Tunel it.",
                       "Tunel commands, from your browser.",
                       "Drop a container to run it."]
    message = choice(message_options)
    return render_template("index.html",message=message)


def base_login(account_id,ignore_regex=None,crystal_ball=False):
    '''base is a general function for "authenticating" a user, meaning retrieving transactions,
    and an account name (and message) given an account_id. A dictionary is returned with these fields
    and if not successful, the "success" key is False, and the message field should be shown to user
    '''
    result = dict()
    if account_id in app.accounts["institution-id"].tolist():
        result["log"] = get_transaction_log(account_id,
                                            ignore_regex=ignore_regex,
                                            crystal_ball=crystal_ball)

        result["name"] = get_account_name(account_id)
        result["message"] = "Welcome to your account, %s" %(result["name"])
        result["success"] = True
        result["id"] = account_id
    else:
        result["message"] = "Sorry, the account %s was not found." %(account_id)
        result["success"] = False
    return result

@app.route("/home/<account_id>")
def home(account_id):
    '''home is the login view after the user has logged in'''    
    account_id = int(account_id)
    result = base_login(account_id)
    if result["success"] == True:
        return render_template("home.html",log=result["log"],
                                           message=result["message"],
                                           account_id=result["id"])  
    else:
        return render_template("index.html",message=result["message"])

@app.route("/login",methods=["POST","GET"])
def login():
    '''login is the first view seen after login'''
    
    if request.method == "POST":
        account = int(request.form["account_id"])
        result = base_login(account)
        if result["success"] == True:
            return render_template("home.html",log=result["log"],
                                               message=result["message"],
                                               account_id=result["id"])  
        else:
            return render_template("index.html",message=result["message"])
    else:
        message = "You must log in first before viewing account home."
    return render_template("index.html",message=message)
    
#--ignore-donuts: The user is so enthusiastic about donuts that they don't want donut spending to come out of their budget. Disregard all donut-related transactions from the spending. You can just use the merchant field to determine what's a donut

@app.route("/donut/<account_id>")
def donut(account_id):
    '''ignore donuts does not include donut costs'''
    account_id = int(account_id)
    result = base_login(account_id,ignore_regex="Krispy Kreme Donuts|DUNKIN")
    if result["success"] == True:
        message = "Your transactions not including donut spending, your majesty!"
        return render_template("home.html",log=result["log"],
                                           message=message,
                                           account_id=result["id"],
                                           ignore_donuts="anything")  
    else:
        return render_template("index.html",message=result["message"])
    return render_template("index.html",message=message)    

# --crystal-ball: We expose a  endpoint, which returns all the transactions that have happened or are expected to happen for a given month. It looks like right now it only works for this month, but that's OK. Merge the results of this API call with the full list from GetAllTransactions and use it to generate predicted spending and income numbers for the rest of this month, in addition to previous months.

@app.route("/crystalball/<account_id>")
def crystalball(account_id):
    '''include projected transactions for future'''
    account_id = int(account_id)
    result = base_login(account_id,crystal_ball=True)
    if result["success"] == True:
        now = datetime.now()
        message = "We've predicted the future for %s-%s!" %(now.year,now.month)
        return render_template("home.html",log=result["log"],
                                           message=message,
                                           account_id=result["id"],
                                           crystal_ball="anything")  
    else:
        return render_template("index.html",message=result["message"])


@app.route('/download/<account_id>/<crystal_ball>/<ignore_donuts>')
def download(account_id,crystal_ball=0,ignore_donuts=0):
    account_id = int(account_id)
    crystal_ball = bool(crystal_ball)
    ignore_donuts = bool(ignore_donuts)
    ignore_regex = None
    if ignore_donuts == True:
        ignore_regex = "Krispy Kreme Donuts|DUNKIN"    
    result = base_login(account_id,crystal_ball=crystal_ball,ignore_regex=ignore_regex)
    if result["success"] == True:    
        return jsonify(result["log"])
    else:
        index()  

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
