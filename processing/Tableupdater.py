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
        tables = ["Clans", "Players", "Wars", "Attacks"]
        for table in tables:
            if dm.fileExists(table):
                await dm.saveToFile(ds.createTable(table), table)

    async def updateTables(self, df):
        ...

    
