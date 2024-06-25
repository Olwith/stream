import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from shapely.geometry import Point, LineString, Polygon
import json

# Initialize session state
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame()
if 'gdf' not in st.session_state:
    st.session_state['gdf'] = gpd.GeoDataFrame(columns=['geometry'])
if 'columns' not in st.session_state:
    st.session_state['columns'] = ['ID', 'name', 'latitude', 'longitude', 'class', 'quantity']

def save_uploaded_file(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state['data'] = df
        st.session_state['columns'] = df.columns.tolist()
        st.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Error: {e}")

def save_uploaded_shapefile(uploaded_file):
    try:
        gdf = gpd.read_file(uploaded_file)
        st.session_state['gdf'] = gdf
        st.success("Shapefile uploaded successfully!")
    except Exception as e:
        st.error(f"Error: {e}")

def add_data(row):
    new_row = pd.DataFrame([row])
    st.session_state['data'] = pd.concat([st.session_state['data'], new_row], ignore_index=True)

def add_geometry(geometry, attributes):
    new_gdf = gpd.GeoDataFrame([attributes], geometry=[geometry])
    st.session_state['gdf'] = pd.concat([st.session_state['gdf'], new_gdf], ignore_index=True)

def save_data_to_csv():
    csv = st.session_state['data'].to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='data.csv',
        mime='text/csv',
    )

def save_shapefile():
    st.session_state['gdf'].to_file("digitized_features.shp")
    st.success("Shapefile saved successfully!")
    with open("digitized_features.shp", "rb") as shp:
        st.download_button(
            label="Download shapefile",
            data=shp,
            file_name="digitized_features.shp",
            mime="application/octet-stream",
        )

def create_map(data, map_type):
    # Initialize the map centered around the mean latitude and longitude of the data
    if not data.empty:
        center_lat = data['latitude'].mean()
        center_lon = data['longitude'].mean()
    else:
        center_lat = -1.2921
        center_lon = 36.8219

    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles=None)

    # Add selected tile layer
    if map_type == 'OpenStreetMap':
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            name='OpenStreetMap',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        ).add_to(m)
    elif map_type == 'Imagery':
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            name='Imagery',
            attr='&copy; <a href="https://www.esri.com">Esri</a> &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        ).add_to(m)
    elif map_type == 'Terrain':
        folium.TileLayer(
            tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
            name='Terrain',
            attr='Map data: &copy; <a href="https://www.opentopomap.org">OpenTopoMap</a> contributors'
        ).add_to(m)

    # Add markers to the map
    for idx, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(f"<b>Name:</b> {row['name']}<br><b>Class:</b> {row['class']}<br><b>Quantity:</b> {row['quantity']}", max_width=300)
        ).add_to(m)

    # Add draw control
    draw = folium.plugins.Draw(export=True)
    draw.add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    return m

st.title("Open Data Collection Kit")

# Upload CSV file
st.sidebar.header("Upload CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    save_uploaded_file(uploaded_file)

# Upload Shapefile
st.sidebar.header("Upload Shapefile")
uploaded_shapefile = st.sidebar.file_uploader("Choose a Shapefile", type=["zip", "shp"])
if uploaded_shapefile is not None:
    save_uploaded_shapefile(uploaded_shapefile)

# Input data manually
st.sidebar.header("Input Data Manually")
id_input = st.sidebar.text_input("ID:")
name_input = st.sidebar.text_input("Name:")
lat_input = st.sidebar.number_input("Latitude:", format="%f")
lon_input = st.sidebar.number_input("Longitude:", format="%f")
class_input = st.sidebar.text_input("Class:")
quantity_input = st.sidebar.number_input("Quantity:", format="%d")
if st.sidebar.button("Add Data"):
    if id_input and name_input and class_input and not pd.isna(lat_input) and not pd.isna(lon_input) and not pd.isna(quantity_input):
        add_data({'ID': id_input, 'name': name_input, 'latitude': lat_input, 'longitude': lon_input, 'class': class_input, 'quantity': quantity_input})
        st.sidebar.success("Data added successfully!")
    else:
        st.sidebar.error("Please fill out all fields.")

# Allow users to add custom columns
st.sidebar.header("Add Custom Columns")
custom_column = st.sidebar.text_input("Custom Column Name:")
if st.sidebar.button("Add Column"):
    if custom_column:
        st.session_state['columns'].append(custom_column)
        st.session_state['data'][custom_column] = ""
        st.sidebar.success(f"Column '{custom_column}' added successfully!")
    else:
        st.sidebar.error("Please enter a column name.")

# Display current data
st.write("### Current Data")
st.write(st.session_state['data'])

# Save data to CSV
st.write("### Save Data")
save_data_to_csv()

# Save shapefile
if not st.session_state['gdf'].empty:
    st.write("### Save Shapefile")
    save_shapefile()

# Visualization options
st.write("### Data Visualization")
chart_type = st.selectbox("Select Chart Type:", ["Line Graph", "Bar Graph", "Pie Chart", "Histogram", "Scatter Plot"])

if not st.session_state['data'].empty:
    if chart_type == "Line Graph":
        fig = px.line(st.session_state['data'], x='name', y='quantity', title='Line Graph of Quantity by Name')
        st.plotly_chart(fig)
    elif chart_type == "Bar Graph":
        fig = px.bar(st.session_state['data'], x='name', y='quantity', title='Bar Graph of Quantity by Name')
        st.plotly_chart(fig)
    elif chart_type == "Pie Chart":
        fig = px.pie(st.session_state['data'], names='name', values='quantity', title='Pie Chart of Quantity by Name')
        st.plotly_chart(fig)
    elif chart_type == "Histogram":
        fig = px.histogram(st.session_state['data'], x='quantity', title='Histogram of Quantity')
        st.plotly_chart(fig)
    elif chart_type == "Scatter Plot":
        fig = px.scatter(st.session_state['data'], x='longitude', y='latitude', size='quantity', color='name', title='Scatter Plot of Locations by Quantity')
        st.plotly_chart(fig)
else:
    st.warning("No data available for visualization")

# Map visualization
st.write("### Map Visualization")
map_type = st.selectbox("Select Map Type:", ["OpenStreetMap", "Imagery", "Terrain"])

if not st.session_state['data'].empty:
    map_object = create_map(st.session_state['data'], map_type)
    output = st_folium(map_object, width=700, height=500)

    if 'last_active_drawing' in output['last_object'] and output['last_object'] is not None:
        drawing = output['last_object']['geometry']
        geom_type = drawing['type']
        coordinates = drawing['coordinates']
        
        if geom_type == 'Point':
            geom = Point(coordinates)
        elif geom_type == 'LineString':
            geom = LineString(coordinates)
        elif geom_type == 'Polygon':
            geom = Polygon(coordinates[0])
        else:
            st.error("Unsupported geometry type")

        st.write("### Add Attributes for Digitized Feature")
        attributes = {}
        for col in st.session_state['columns']:
            attributes[col] = st.text_input(f"Enter value for {col}:")
        
        if st.button("Save Feature"):
            add_geometry(geom, attributes)
            st.success("Feature saved successfully!")
else:
    st.warning("No data available for map visualization")
