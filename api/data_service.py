import api.client as c
import pandas as pd
import processing.datamanager as dm
from datetime import datetime
class getTables:
    def __init__(self):
        self.api = c.APIManager()

    def getClantable(self, clantag):
        clantag = c.urlTag(clantag)
        responseData = self.api.getResponse(f"{self.api.baseUrl}clans/{clantag}")
        clanData = createTable("Clans")
        for col in clanData:
            if col in responseData:
                clanData[col].append(responseData[col])
            else:
                clanData[col].append(0)
        clanData = pd.DataFrame(clanData)
        return clanData
    
    def getMemberTable(self, clantag):
        clantag = c.urlTag(clantag)
        responseData = self.api.getResponse(f"{self.api.baseUrl}clans/{clantag}")
        memberDict = createTable("Players")
        rawMemberList = responseData["memberList"]
        for i in range(len(rawMemberList)):
            for col in memberDict:
                memberDict[col].append(rawMemberList[i][col])
        memberDict = pd.DataFrame(memberDict)
        memberDict["role"] = memberDict["role"].replace("admin", "elder")
        return memberDict
    
    def getWartable(self, clantag):
        clantag  = c.urlTag(clantag)
        responseData = self.api.getResponse(f"{self.api.baseUrl}clans/{clantag}/currentwar")
        warDict = createTable("Wars")
        if "notInWar" != responseData["state"]:
            warDict["startTime"].append(datetime.fromisoformat(responseData["startTime"].replace("Z", "+00:00")))
            warDict["clantag1"].append(responseData["clan"]["tag"])
            warDict["clantag2"].append(responseData["opponent"]["tag"])
            warDict["stars"].append(responseData["clan"]["stars"])
            warDict["percentage"].append(responseData["clan"]["destructionPercentage"])
            warDict["opponentStars"].append(responseData["opponent"]["stars"])
            warDict["opponentPercentage"].append(responseData["opponent"]["destructionPercentage"])
        warDict = pd.DataFrame(warDict)
        return warDict
    

    #gets the Attacktable for the current war of the selected clan:
    #The information in this table includes:
    #attackertag, attackername, defendertag, warclantag, wardate, stars, percentage, and attacknum. The attackertag, wardate and attacknum form the primary Key
    #clantag and wardate are foreign key from the clanwar table
    #attackertag is a forgein key from the playertable
    def getAttacktable(self, clantag):
        clantag = c.urlTag(clantag)
        responseData = self.api.getResponse(f"{self.api.baseUrl}clans/{clantag}/currentwar")
        attackDict = createTable("Attacks")
        if "notInWar" != responseData["state"]:
            rawAttackList = responseData["clan"]["members"]
            for u in range(len(rawAttackList)):
                if "attacks" in rawAttackList[u]:
                    for i in range(len(rawAttackList[u]["attacks"])):
                        attackDict["attackertag"].append(rawAttackList[u]["tag"])
                        attackDict["attackername"].append(rawAttackList[u]["name"])
                        attackDict["attacknum"].append(i+1)
                        attackDict["warclantag"].append(responseData["clan"]["tag"])
                        attackDict["wardate"].append(datetime.fromisoformat(responseData["startTime"].replace("Z", "+00:00")))
                        attackDict["stars"].append(rawAttackList[u]["attacks"][i]["stars"])
                        attackDict["percentage"].append(rawAttackList[u]["attacks"][i]["destructionPercentage"])
                    if len(rawAttackList[u]["attacks"]) == 1:
                        attackDict["attackertag"].append(rawAttackList[u]["tag"])
                        attackDict["attackername"].append(rawAttackList[u]["name"])
                        attackDict["attacknum"].append(2)
                        attackDict["warclantag"].append(responseData["clan"]["tag"])
                        attackDict["wardate"].append(datetime.fromisoformat(responseData["startTime"].replace("Z", "+00:00")))
                        attackDict["stars"].append(0)
                        attackDict["percentage"].append(0)
                else:
                    for i in 2:
                        attackDict["attackertag"].append(rawAttackList[u]["tag"])
                        attackDict["attackername"].append(rawAttackList[u]["name"])
                        attackDict["attacknum"].append(i+1)
                        attackDict["warclantag"].append(responseData["clan"]["tag"])
                        attackDict["wardate"].append(datetime.fromisoformat(responseData["startTime"].replace("Z", "+00:00")))
                        attackDict["stars"].append(0)
                        attackDict["percentage"].append(0)

            attackDict = pd.DataFrame(attackDict)
            return attackDict


class newData:
    def __init__(self):
        self.dm = dm.Datamanager()
        self.gt = getTables()

    def addNewClan(self, df, tag):
        newData = self.gt.getClantable(tag)
        newDf = self.dm.upsert(df, newData, "tag")
        return newDf
    
    def addNewWar(self, df, tag):
        newData = self.gt.getWartable(tag)
        newDf = self.dm.upsert(df, newData, ["startTime", "clantag1"])
        return newDf
    
    def addNewAttacks(self, df, tag):
        newData = self.gt.getAttacktable(tag)
        newDf = self.dm.upsert(df, newData, ["wardate", "attackertag", "attacknum"])
        return newDf


class updateTables:
    def __init__ (self):
        self.gt = getTables()
        self.dm = dm.Datamanager()

    def updateClanTable(self, df):
        clantags = df["tag"].values.tolist()
        for clantag in clantags:
            newClanData = self.gt.getClantable(clantag)
            df = self.dm.upsert(df, newClanData, "tag")
        return df
    
    def updatecurrentWar(self, df, clansdf):
        clantags = clansdf["tag"].values.tolist()
        for clantag in clantags:
            newWarData = self.gt.getWartable(clantag)
            df = self.dm.upsert(df, newWarData, ["startTime", "attackertag", "attacknum"])
        return df



    def updateTable(self, Tablename):
        pass

#creates a Table with predefined column names based on Keyword you use
def createTable(tablename):
    Clans = {"tag" : [], "name" : [], "members" : [], "clanLevel" : [], "warWins" : [], "warTies" : [], "warLosses": [], "isWarLogPublic" : []}
    Players = {"tag" : [], "name" : [], "clantag" : [], "role" : [], "townHallLevel" : [], "trophies" : [], "clanRank" : [], "donationsReceived" : [], "donations" : [], "expLevel" : []}
    Wars = {"startTime": [], "clantag1" : [], "clantag2" : [], "stars" : [], "percentage": [], "opponentStars" : [], "opponentPercentage" : []}
    Attacks = {"attackertag" :[], "attackername" : [], "attacknum" : [], "warclantag" : [], "wardate" : [], "stars" : [], "percentage" : []}
    Tables = {"Clans" : Clans, "Players" : Players, "Wars" : Wars, "Attacks" : Attacks}
    return Tables[tablename]