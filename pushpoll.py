#!/usr/bin/python3
#
# Symantec VIP Push for End-User Approval
# 12/2018 - https://github.com/bdwilson/VIPSupportPush
# 
# sudo apt-get install python3 python3-pip python3-suds python3-websocket python3-urllib3 python3-requests python3-botocore
# sudo pip3 install securitas
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

parser = argparse.ArgumentParser()
parser.add_argument("--user", "-u", help="Send a push request to this userid", required=True)
parser.add_argument("--message", "-m", help="Message for push request", required=True)
parser.add_argument("--title", "-t", help="Title for push request", required=True)
args = parser.parse_args()
if not args.user:
    parser.print_help()
    sys.exit(1)

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
if args.message:
    data["displayParameters"].append({"Key":"display.message.text", "Value": args.message})

if args.title:
    data["displayParameters"].append({"Key":"display.message.title", "Value": args.title})

response = user_services_object.authenticateUserWithPush("SupportPush",args.user, None, data)

status=user_services_object.getResponseValue(response,'status')
statusMessage=user_services_object.getResponseValue(response,'statusMessage')

if (status == '6040'):
    print("Push Initiated for", args.user)
    transaction=user_services_object.getResponseValue(response,'transactionId')
    request=user_services_object.getResponseValue(response,'requestId')
else:
    print("Error sending push to", args.user, ":" , statusMessage)
    exit()

isExit = False
isError = False

for sec in range(1,60 // 3):
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
        isExit = True
        break

    if "0000" in status: # ignore this first status for polling connection
        continue
    elif "7000" in status:
        print("SUCCESS! Push Accepted by", args.user)
        isExit = True
        break
    elif "7001" in status:
        print("Waiting for response...")
        continue
    elif "7002" in status:
        print("Push Denied by", args.user)
        isExit = True
        break
    else:
        isError = True
