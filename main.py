import api.data_service as ds
import processing.datamanager as dmanager
import streamlit as st
import pandas as pd

gt = ds.getTables()
ut = ds.updateTables()
dm = dmanager.Datamanager()
nd = ds.newData()

wars_T = ds.createTable("Attacks")
Wars = pd.DataFrame(wars_T)
print(Wars.head())
dm.saveToFile(Wars, "Attacks")

if __name__ == "__main__":
    Wars = dm.readFile("Attacks")
    if Wars.empty:
        dm.saveToFile(gt.getAttacktable(input("enter Clantag:")), "Attacks")
        Wars = dm.readFile("Attacks")
    print(Wars)
    addclan = True
    while addclan == True:
        Wars = nd.addNewWar(Wars, input("enter another Clantag:"))
        dm.saveToFile(Wars, "Clans")
        print(Wars)
        addclan = input("Do you want to add another Clan to the table? (y/n):").lower().startswith('y')

