#!/usr/bin/python3
#
# Symantec VIP Push for End-User Approval - Flask web app
#
# 12/2018 - https://github.com/bdwilson/VIPSupportPush
#
# sudo apt-get install python3 python3-pip python3-suds python3-websocket python3-urllib3 python3-requests python3-botocore
# sudo pip3 install securitas
# sudo pip3 install flask
# sudo pip3 install wtforms
#
# Adjust message & title variables below, as well as IP/port information towards the bottom.
# 
import time
import os
import argparse
import urllib.parse
from suds.client import Client
from symantec_package.lib.userService.SymantecUserServices import SymantecUserServices
from symantec_package.lib.queryService.SymantecQueryServices import SymantecQueryServices
from urllib.request import pathname2url
from symantec_package.HTTPHandler import HTTPSClientCertTransport
from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

# Change these for your usecase
message="This is a message"
title="This is a title"

# App config.
DEBUG = False
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176abcd1234'

def sendPush(userid):

    user_services_url = urllib.parse.urljoin('file:', pathname2url(os.path.abspath('./wsdl_files/vipuserservices-auth-1.7.wsdl')))
    user_services_client = Client(user_services_url,
      transport = HTTPSClientCertTransport( './privateKey_nopass.pem', './publicCert.pem'))
    query_services_url = urllib.parse.urljoin('file:', pathname2url(os.path.abspath('./wsdl_files/vipuserservices-query-1.7.wsdl')))
    query_services_client = Client(query_services_url,
      transport = HTTPSClientCertTransport( './privateKey_nopass.pem', './publicCert.pem'))

    user_services_object = SymantecUserServices(user_services_client)
    query_services_object = SymantecQueryServices(query_services_client)

    data = {}
    data["displayParameters"] = []
    data["displayParameters"].append({"Key":"display.message.text", "Value": message})
    data["displayParameters"].append({"Key":"display.message.title", "Value": title})

    response = user_services_object.authenticateUserWithPush("SupportPush",userid, None, data)

    status=user_services_object.getResponseValue(response,'status')
    statusMessage=user_services_object.getResponseValue(response,'statusMessage')

    if (status == '6040'):
        print("Push Initiated for", userid)
        transaction=user_services_object.getResponseValue(response,'transactionId')
        request=user_services_object.getResponseValue(response,'requestId')
    else:
        print("Error sending push to", userid, ":" , statusMessage)
        return("Error: Unable to send push to " + userid + ": " + statusMessage) 

    isExit = False
    isError = False

    for sec in range(1,30 // 3):
        if isExit:
            break
        time.sleep(3) # NEED NEW SOLUTION for querying on interval in python
        poll_status = query_services_object.pollPushStatus(request,transaction)
        transaction_status = query_services_object.getResponseValue(poll_status,'transactionStatus')
        for tup in transaction_status:
            status=tup[1]
            msg=tup[2]

        if isError:
            print("\n\tError: " + msg)
            return("Error: Unable to validate user: " + msg) 
            isExit = True
            break

        if "0000" in status: # ignore this first status for polling connection
            continue
        elif "7000" in status:
            print("SUCCESS! Push Accepted by " + userid)
            return("Push Accepted by "+ userid)
            isExit = True
            break
        elif "7001" in status:
            print("Waiting for response...")
            continue
        elif "7002" in status:
            print("Push Denied by", userid)
            return("Error: Push denied by "+ userid)
            isExit = True
            break
        else:
            isError = True
    return("Error: Request to " + userid + " timed out.")
 
class ReusableForm(Form):
    userid = TextField('UserID:', validators=[validators.Regexp(regex=r'^[0-9A-Za-z-_.@]+$')])

 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
 
    print(form.errors)
    if request.method == 'POST':
        userid=request.form['userid']
        print(userid)
 
        if form.validate():
             # Save the comment here.
            val=sendPush(userid)
            flash(val)
        else:
            flash('Error: A userid may only consist of letters, numbers, and [-_@.]. ')
 
    return render_template('vip.html', form=form)
 
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


