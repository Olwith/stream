import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Function to read shapefiles
def read_shapefile(file):
    try:
        gdf = gpd.read_file(file)
        return gdf
    except Exception as e:
        st.error(f"Error reading the shapefile: {e}")
        return None

# Streamlit app
st.title("Spatial Data Collection and Visualization App")

# File uploader
uploaded_file = st.file_uploader("Upload a Shapefile (zip format containing .shp, .shx, .dbf, etc.)", type="zip")

if uploaded_file is not None:
    # Unzipping the uploaded file
    with open("uploaded_file.zip", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    import zipfile
    with zipfile.ZipFile("uploaded_file.zip", "r") as zip_ref:
        zip_ref.extractall("temp_shapefile")
    
    # Reading the shapefile
    shapefile_path = "temp_shapefile"
    gdf = read_shapefile(shapefile_path)
    
    if gdf is not None:
        st.subheader("Shapefile Data")
        st.write(gdf)
        
        # Visualization on a map
        st.subheader("Map Visualization")
        map_center = [gdf.geometry.iloc[0].centroid.y, gdf.geometry.iloc[0].centroid.x]
        m = folium.Map(location=map_center, zoom_start=10)

        # Add the shapefile to the map
        folium.GeoJson(gdf).add_to(m)
        
        # Display the map
        st_folium(m, width=700, height=500)
else:
    st.info("Please upload a shapefile to visualize.")

st.sidebar.header("About")
st.sidebar.info("This app allows you to upload and visualize spatial data in shapefile format.")
