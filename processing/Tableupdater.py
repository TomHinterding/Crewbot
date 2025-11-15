import api.data_service as ds
import processing.datamanager as dmanager
import streamlit as st
import pandas as pd

gt = ds.getTables()
ut = ds.updateTables()
dm = dmanager.Datamanager()
nd = ds.newData()



class Tableupdater():
    def __init__():
        pass

    async def initializeTables(self):
        await dm.saveToFile(ds.createTable("Clans"), "Clans")
        await dm.saveToFile(ds.createTable("Players"), "Players")
        await dm.saveToFile(ds.createTable("Wars"), "Wars")
        await dm.saveToFile(ds.createTable("Attacks"), "Attacks")

    async def updateTables(self, df):
        ...

    
