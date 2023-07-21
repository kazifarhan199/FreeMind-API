
import pandas as pd
import requests

url = 'http://localhost:52000/recommendations/label/create/'

def load_data():
    file_path = input("Enter the path to the file to load: ")
    token = input("Token: ")
    device_token = input("Device Token: ")
    headers = {"Content-Type": "application/json; charset=utf-8", 'Authorization': f'Token {token}', 'Device': device_token}
    df = pd.read_csv(file_path)
    df = df.fillna('.')
    i = 1
    for row in df.values:
        data = {
            'id': i,
            'name' : row[0],
            'type' : row[1],
            'reason' : row[2],
            'link' : row[3],
            'is_label' : row[4],
            'is_coupuled' : row[5],
            'source_based' : row[6],
            'social_based' : row[7],
            'hybrid_based' : row[8],
            'group_based': row[9],
        }
        i+=1
        resp = requests.post(url, json = data, headers=headers)
        print(resp, '--', resp.text)

load_data()