import requests as req
import json
from dotenv import load_dotenv
import os
load_dotenv()
eingabe = "%23YV0LULVC"
baseUrl = "https://api.clashofclans.com/v1"
API_TOKEN = os.getenv("COC_API_TOKEN")
print(API_TOKEN)
header = {"Authorization" : f"Bearer {API_TOKEN}"}
url = f"{baseUrl}/clans?name={eingabe}"
response = req.get(url, headers = header)
if response.status_code == 200:
    response_data = response.json()
    clans = response_data["items"][0]
    print(clans["name"], clans["tag"])
else:
    response.raise_for_status()