Symantec VIP Push for End-User Approval
=======
<i>Imitation is the sincerest form of flattery.</i><br><br>
One of the challenges of being in IT support is verifying the identity of the person who's requesting remote assistance. Often employees call into a support desk and require account assitance, need a password reset, or some other security-related request. How can the support staff be sure that the person they're helping is who they say they are?
<br><br>
We've leveraged VIP to do this for some time, but it required the reqester to provide the code displayed in the VIP app on their phone, then the support person had to properly transfer their code and enter it, along with heir userid into a radius authentication web-form - all within 30 seconds. This process is definately prone to error, so when [Duo released](https://duo.com/blog/bringing-feature-requests-to-life-duo-push-verification) their "Push to Verify" feature, I set out to create something similar for Symantec VIP push MFA token.
<br><br>
This feature works the same way with VIP. The person initiating the request can verify the identity of a person with a single push request to the end-user device.  They can also provide context in the push message on what the request is for to make the request more legitimate to the end-user. Of course this process requires the end-user to have the VIP app on their device and push features enabled. 

![Push Notification](https://cdn-std.dprcdn.net/files/acc_601089/izsQce)

*I'm not a python programmer, much less someone who can do web frontends, but this would be a good candidate for a web/GUI front-end to ease access for support personnel. If you write a web front-end, please let me know so I can link to it.*

Requirements
------------
- [Securitas](https://github.com/ArrenH/Securitas) Python SDK for Symantec VIP API
- [Symantec VIP Account](https://vip.symantec.com/)
- Symantec VIP adminstrative access (or someone to generate a VIP communications certificate & key for you; see Securitas docs on how to extract the private key and cert, as well as removing the password from the private key)
- Python 3 these Modules: python3-pip, python3-suds, python3-websocket, python3-urllib3, python3-requests, python3-botocore
- You'll need to know the userid for the person as it exists within the VIP Manager. This isn't always first.last@domain, it could be SAMAccountName (short userid).

Installation & Usage
--------------------
It was easier for me to leverage docker to build and test this to get the correct python dependencies:
1. <code># docker pull debian</code>
2. <code># docker run --name debian -t debian /bin/bash </code>
3. <code># docker exec -it debian /bin/bash</code>
4. <code># apt-get install python3 python3-pip python3-suds python3-websocket python3-urllib3 python3-requests python3-botocore git</code>
5. <code># pip3 install securitas</code>
6. <code># git clone https://github.com/bdwilson/VIPSupportPush; cd VIPSupportPush</code>
7. Make sure your VIP key and cert are in this directory named <code>privateKey_nopass.pem</code> and <code>publicCert.pem</code> respectively.
8. Validate someone:
<pre># ./pushpoll.py -u vipUserId -m "Please verify your identity by approving this request." -t "YourCompany Service Desk"
Push Initiated for vipUserId
Waiting for response...
Waiting for response...
Waiting for response...
SUCCESS! Push Accepted by vipUserId
</pre>
<pre># ./pushpoll.py -u vipUserId -m "Please verify your identity by approving this request." -t "YourCompany Service Desk"
Push Initiated for vipUserId
Waiting for response...
Push Denied by vipUserId
</pre>

Bugs/Contact Info
-----------------
Bug me on Twitter at [@brianwilson](http://twitter.com/brianwilson) or email me [here](http://cronological.com/comment.php?ref=bubba).
