import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic
from tempfile import TemporaryDirectory
import os

# Constants
FARE_PER_KM = 5  # Fare rate per kilometer in Ksh

# Title of the Streamlit app
st.title("GIS Facilities Database for Bus Company")

# Sidebar for uploading the facilities data
st.sidebar.title("Upload Data")
uploaded_files = st.sidebar.file_uploader(
    "Choose a CSV, GeoJSON, or Shapefile (upload all shapefile components together)",
    type=["csv", "geojson", "shp", "shx", "dbf", "prj"],
    accept_multiple_files=True
)

if uploaded_files:
    # Handle shapefile upload
    shapefile_extensions = {"shp", "shx", "dbf", "prj"}
    uploaded_file_types = {file.name.split('.')[-1] for file in uploaded_files}
    
    if shapefile_extensions.issubset(uploaded_file_types):
        with TemporaryDirectory() as tmpdir:
            for uploaded_file in uploaded_files:
                with open(os.path.join(tmpdir, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            gdf = gpd.read_file(os.path.join(tmpdir, [f.name for f in uploaded_files if f.name.endswith('.shp')][0]))
    else:
        # Read the uploaded file into a GeoDataFrame or DataFrame
        uploaded_file = uploaded_files[0]
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
            # Convert DataFrame to GeoDataFrame
            gdf = gpd.GeoDataFrame(
                data, geometry=gpd.points_from_xy(data.longitude, data.latitude))
        elif uploaded_file.name.endswith('.geojson'):
            gdf = gpd.read_file(uploaded_file)
    
    # Display the uploaded data
    st.write("Uploaded Data:")
    st.write(gdf.head())

    # Create a Folium map centered around the mean coordinates of the facilities
    m = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=12)
    
    # Add markers for each facility
    for _, row in gdf.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=row['facility_name'] if 'facility_name' in row else '',
            tooltip=row['facility_name'] if 'facility_name' in row else ''
        ).add_to(m)
    
    # Display the map
    folium_static(m)
else:
    st.write("Please upload a CSV, GeoJSON, or Shapefile containing the facilities data.")

# Example template for CSV upload
st.sidebar.markdown("""
### Example CSV Format
""")

# Placeholder for a list of places in Kenya
places = {
    "Nairobi": (-1.286389, 36.817223),
    "Mombasa": (-4.05, 39.6667),
    "Nakuru": (-0.3, 36.0667),
    "Eldoret": (0.5167, 35.2833),
    "Kisumu": (-0.0833, 34.7667),
    "Kikuyu": (-1.25, 36.6667),
    "Lunga-Lunga": (-4.555, 39.1231),
    "Habaswein": (1.01, 39.49),
    "Ongata Rongai": (-1.4, 36.77),
    "Garissa": (-0.4569, 39.6583),
    "Molo": (-0.25, 35.7333),
    "Kitenkela": (-1.5167, 36.85),
    "Kiambu": (-1.1667, 36.8167),
    "Ramu": (3.9375, 41.2203),
    "Kilifi": (-3.6333, 39.85),
    "Malindi": (-3.2236, 40.13),
    "Vihiga": (0.05, 34.725),
    "Machakos": (-1.5167, 37.2667),
    "Kisii": (-0.6833, 34.7667),
    "Ngong": (-1.3667, 36.6333),
    "Mumias": (0.3333, 34.4833),
    "Thika": (-1.0396, 37.09),
    "Nyeri": (-0.4167, 36.95),
    "Kakamega": (0.2822, 34.754),
    "Wajir": (1.75, 40.05),
    "Ukunda": (-4.2875, 39.5661),
    "Nandi Hills": (0.1003, 35.1764),
    "Narok": (-1.0833, 35.8667),
    "Embu": (-0.5389, 37.4583),
    "Kitale": (1.0167, 35),
    "Wundanyi": (-3.3983, 38.3603),
    "El Wak": (2.8028, 40.9275),
    "Wote": (-1.7833, 37.6333),
    "Kimilili": (0.7833, 34.7167),
    "Bungoma": (0.5667, 34.5667),
    "Isiolo": (0.35, 37.5833),
    "Meru": (0.05, 37.65),
    "Webuye": (0.6167, 34.7667),
    "Iten": (0.6731, 35.5083),
    "Homa Bay": (-0.5167, 34.45),
    "Rumuruti": (0.26, 36.5363),
    "Maralal": (1.1, 36.7),
    "Busia": (0.4633, 34.1053),
    "Mandera": (3.9167, 41.8333),
    "Kericho": (-0.3692, 35.2839),
    "Kitui": (-1.3667, 38.0167),
    "Lamu": (-2.2694, 40.9022),
    "Kajiado": (-1.85, 36.7833),
    "Kapsabet": (0.3333, 35.1667),
    "Marsabit": (2.3333, 37.9833),
    "Lodwar": (3.1167, 35.6),
    "Kerugoya": (-0.5, 37.2833),
    "Kwale": (-4.1744, 39.4603),
    "Hola": (-1.5, 40.0333),
    "Mwatate": (-3.5047, 38.3778),
    "Kabarnet": (0.494, 35.744),
    "Migori": (-1.0634, 34.4731),
    "Nyamira": (-0.521, 34.914),
    "Sotik Post": (-0.7813, 35.3416),
    "Murang’a": (-0.7167, 37.15),
    "Siaya": (0.0667, 34.2833),
    "Kapenguria": (1.2333, 35.1167),
    "Ol Kalou": (-0.273, 36.378)
}

# Boarding and dropping points selection
st.sidebar.title("Calculate Fare and Distance")
boarding_point = st.sidebar.selectbox("Select Boarding Point", list(places.keys()))
dropping_point = st.sidebar.selectbox("Select Dropping Point", list(places.keys()))

if boarding_point and dropping_point:
    if boarding_point in places and dropping_point in places:
        # Get coordinates for the selected places
        coords_1 = places[boarding_point]
        coords_2 = places[dropping_point]
        
        # Calculate the distance
        distance = geodesic(coords_1, coords_2).kilometers
        fare = distance * FARE_PER_KM
        
        # Display the distance and fare
        st.sidebar.write(f"Distance between {boarding_point} and {dropping_point} is {distance:.2f} km")
        st.sidebar.write(f"Estimated fare: Ksh {fare:.2f}")
        
        # Visualize the points on the map
        m = folium.Map(location=[(coords_1[0] + coords_2[0]) / 2, (coords_1[1] + coords_2[1]) / 2], zoom_start=7)
        
        # Add markers for boarding and dropping points
        folium.Marker(coords_1, popup=f"Boarding Point: {boarding_point}", tooltip="Boarding Point").add_to(m)
        folium.Marker(coords_2, popup=f"Dropping Point: {dropping_point}", tooltip="Dropping Point").add_to(m)
        
        # Draw a line between the points
        folium.PolyLine([coords_1, coords_2], color="blue", weight=2.5, opacity=1).add_to(m)
        
        # Display the map
        folium_static(m)
    else:
        st.sidebar.write("Please enter valid place names from the list.")
else:
    st.sidebar.write("Please enter both boarding and dropping points.")

# Upload bus schedules
st.sidebar.title("Upload Bus Schedules")
bus_schedule_file = st.sidebar.file_uploader("Choose a CSV file with bus schedules", type="csv")

if bus_schedule_file:
    bus_schedules = pd.read_csv(bus_schedule_file)
    st.write("Bus Schedules:")
    st.write(bus_schedules)

    # Filter buses based on boarding and dropping points
    if boarding_point and dropping_point:
        available_buses = bus_schedules[
            (bus_schedules['boarding_point'] == boarding_point) &
            (bus_schedules['dropping_point'] == dropping_point)
        ]
        st.write(f"Available buses from {boarding_point} to {dropping_point}:")
        st.write(available_buses)
else:
    st.sidebar.write("Please upload a CSV file containing bus schedules.")

# Example template for bus schedules CSV upload
st.sidebar.markdown("""
### Example Bus Schedules CSV Format
""")

