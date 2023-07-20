import requests
import json

pre = 'user'
start_number = 101
group_name = f"Group {start_number}"
base_url = "https://csgrad08.d.umn.edu"


def createUser(username, password):
    url = f'{base_url}/accounts/register/'
    myobj = {'username': username, 'password': password, 'email': f'{username}@email.com', 'devicetoken':'token', 'devicename':'name', 'devicetype':'android'}
    x = requests.post(url, json = myobj)
    _respose = json.loads(x.text)
    print(_respose)
    return _respose['email'] ,_respose['token']



def createGroup(g_name, token):
    url = f'{base_url}/groups/create/'
    myobj = {'group_name': g_name}
    headers = {"Content-Type": "application/json; charset=utf-8", 'Authorization': f'Token {token}', 'Device': 'token'}
    x = requests.post(url, json = myobj, headers=headers)
    _respose = json.loads(x.text)
    print(_respose)
    return _respose['id']

def addToGroup(gid, email, token):
    url = f'{base_url}/groups/members/?group={gid}'
    myobj = {'email': email}
    headers = {"Content-Type": "application/json; charset=utf-8", 'Authorization': f'Token {token}', 'Device': 'token'}
    x = requests.post(url, json = myobj, headers=headers)
    _respose = json.loads(x.text)
    print(_respose)
    return _respose

emails = []

email, _ = createUser(f'{pre}{start_number}', 'Pass@123')
emails.append(email)
start_number += 1

email, _ = createUser(f'{pre}{start_number}', 'Pass@123')
start_number += 1
emails.append(email)

_, token = createUser(f'{pre}{start_number}', 'Pass@123')

gid = createGroup(group_name, token)

for email in emails:
    addToGroup(gid, email, token)
