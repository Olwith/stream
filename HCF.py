import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Function to load the CSV file
@st.cache
def load_data(file):
    data = pd.read_csv(file)
    # Drop rows with missing latitude or longitude
    data = data.dropna(subset=['latitude', 'longitude'])
    return data

# Function to create a Folium map with different layers
def create_map(data):
    # Initialize the map centered around Kenya
    m = folium.Map(location=[1.2921, 36.8219], zoom_start=6, tiles=None)
    
    # Add tile layers with attribution
    folium.TileLayer('openstreetmap', name='OpenStreetMap', 
                     attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors').add_to(m)
    folium.TileLayer('Stamen Terrain', name='Terrain', 
                     attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
    folium.TileLayer('Stamen Toner', name='Toner', 
                     attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
    folium.TileLayer('Stamen Watercolor', name='Watercolor', 
                     attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.').add_to(m)
    folium.TileLayer('CartoDB positron', name='CartoDB Positron', 
                     attr='&copy; <a href="https://carto.com/attributions">CARTO</a>').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='CartoDB Dark Matter', 
                     attr='&copy; <a href="https://carto.com/attributions">CARTO</a>').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
        name='Esri Satellite', 
        attr='&copy; <a href="https://www.esri.com">Esri</a> &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    ).add_to(m)
    
    # Add markers to the map
    for idx, row in data.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(f"<b>Name:</b> {row['name']}<br><b>Type:</b> {row['operator_type']}<br><b>Amenity:</b> {row['amenity']}", max_width=300)
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

# Create a Streamlit app
def main():
    st.title("Health Facilities in Kenya")
    
    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    
    if uploaded_file is not None:
        # Load the data
        data = load_data(uploaded_file)
        
        if data.empty:
            st.error("No valid data to display. Please check your CSV file.")
        else:
            # Display the dataframe
            st.write("### Health Facilities Data", data)
            
            # Create and display the map
            st.write("### Map of Health Facilities")
            map_object = create_map(data)
            st_folium(map_object, width=700, height=500)
            
            # Query functionality
            st.write("### Query Health Facilities")
            
            # Search by name
            name = st.text_input("Search by name:")
            if name:
                result = data[data['name'].str.contains(name, case=False, na=False)]
                st.write(result)
            
            # Filter by type
            types = data['operator_type'].unique()
            selected_type = st.selectbox("Filter by type:", options=types)
            if selected_type:
                filtered_data = data[data['operator_type'] == selected_type]
                st.write(filtered_data)

if __name__ == "__main__":
    main()
