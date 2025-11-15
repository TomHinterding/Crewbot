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
    pass
