import requests as req
import json

class APIManager:
    def __init__(self, baseUrl = "https://api.clashofclans.com/v1/", apiFile = "token.env", ):
        self.baseUrl = baseUrl
        with open(apiFile, "r") as f:
            API_TOKEN = f.read().strip()
        self.header = {"Authorization" : f"Bearer {API_TOKEN}"}


    def getResponse(self, url):
        response = req.get(url, headers = self.header)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            print(response_data)
            return response_data
        else:
            response.raise_for_status()

def urlTag(tag):
    return tag.replace('#', '%23')
