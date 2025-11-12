import requests as req
import json
from dotenv import load_dotenv
import os

class APIManager:
    def __init__(self, baseUrl = "https://api.clashofclans.com/v1/"):
        self.baseUrl = baseUrl
        API_TOKEN = os.getenv("COC_API_TOKEN")
        print(API_TOKEN)
        self.header = {"Authorization" : f"Bearer {API_TOKEN}"}


    def getResponse(self, url):
        response = req.get(url, headers = self.header)
        if response.status_code == 200:
            response_data = response.json()
            return response_data
        else:
            response.raise_for_status()

def urlTag(tag):
    return tag.replace('#', '%23')
