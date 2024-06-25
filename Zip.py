# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 08:31:53 2024

@author: Olwith
"""
import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import tempfile
import zipfile
import os

def csv_to_gdf(csv_file):
    df = pd.read_csv(csv_file)
    gdf = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.longitude,df.latitude))
    gdf.crs = "EPSG:4326"
    return gdf
def gdf_to_kml(gdf):
    kml_file = tempfile.NamedTemporaryFile(suffix='.kml',delete=False)
    gdf.to_file(kml_file.name,driver='KML')
    return kml_file.name
def gdf_to_shapefile_zip(gdf):
    with tempfile.TemporaryDirectory()as tmpdir:
        shapefile_path = os.path.join(tmpdir,"data.shp")
        gdf.to_file(shapefile_path,driver="ESRI Shapefile")
        
        zip_path = tempfile.NamedTemporaryFile(suffix='.zip',delete=False)
        with zipfile.Zipfile(zip_path.name,'w') as zf:
            for filename in os.listdir(tmpdir):
                zf.write(os.path.join(tmpdir,filename), arcname=filename)
        return zip_path.name
def main():
    st.title("CSV to Map,KML and Shapefile Converter")
    
    uploaded_file =st.file_uploader("Choose a CSV file",type="csv")
    if uploaded_file is not None:
        gdf = csv_to_gdf(uploaded_file)
        
        st.map(gdf)
        
        if st.button("Export as KML"):
            kml_path = gdf_to_kml(gdf)
            with open(kml_path,"rb") as file:
                btn = st.download_button(
                      label="Download KML",
                      data = file,
                      file_name="data.kml",
                      mime ="application/vnd.google-earth.kml+xml"
                    )
        if st.button("Export as Shapefile ZIP"):
            shapefile_zip_path = gdf_to_shapefile_zip(gdf)
            with open(shapefile_zip_path,"rb") as file:
                btn = st.download_button(
                      label="Download Shapefile ZIP",
                      data = file,
                      file_name="data.zip",
                      mime ="application/zip"
                    )
if __name__ == "__main__":
    main()


