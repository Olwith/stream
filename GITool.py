import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import networkx as nx
import osmnx as ox
from geopy.distance import geodesic
from tempfile import TemporaryDirectory
import os


# Constants
FARE_PER_KM = 12  # Fare rate per kilometer in Ksh

# Title of the Streamlit app
st.title("GIS Facilities Database")

# Function to add markers to the Folium map
def add_markers_to_map(map_obj, points, color='blue'):
    for point in points:
        folium.Marker(
            location=point[::-1],  # reverse the coordinates for Folium
            icon=folium.Icon(color=color),
        ).add_to(map_obj)

# Function to plot route on the map
def plot_route_on_map(map_obj, route_nodes, route_color='blue'):
    route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route_nodes]
    folium.PolyLine(locations=route_coords, color=route_color, weight=5).add_to(map_obj)

# Sidebar for uploading the facilities data
st.sidebar.title("Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload a CSV file", type=["csv"]
)

if uploaded_file is not None:
    try:
        # Explicitly specify encoding and handle errors
        gdf = pd.read_csv(uploaded_file, encoding='utf-8', error_bad_lines=False)
        
        # Convert to GeoDataFrame assuming latitude and longitude columns are present
        gdf['geometry'] = gpd.points_from_xy(gdf['longitude'], gdf['latitude'])
        gdf = gpd.GeoDataFrame(gdf, geometry='geometry')

        # Display the uploaded data
        st.write("Uploaded Data:")
        st.write(gdf.head())

        # Create a Folium map centered around the mean coordinates of the facilities
        m = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=10)

        # Add markers for each facility
        for _, row in gdf.iterrows():
            folium.Marker(
                location=[row.geometry.y, row.geometry.x],
                popup=row['facility_name'] if 'facility_name' in row else '',
                tooltip=row['facility_name'] if 'facility_name' in row else ''
            ).add_to(m)

        # Display the map
        folium_static(m)

    except UnicodeDecodeError:
        st.error("Error: Failed to decode the CSV file. Please ensure the file is encoded properly.")
    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.write("Please upload a CSV file.")

# Function to load road network from OpenStreetMap
@st.cache
def load_road_network(place):
    G = ox.graph_from_place(place, network_type='drive')
    return G

# Route Analysis Layer
st.sidebar.title("Route Analysis")
route_analysis = st.sidebar.button("Perform Route Analysis")

if route_analysis and 'gdf' in locals():
    st.sidebar.subheader("Select Facilities for Route Analysis")
    facility_names = gdf['facility_name'].tolist()
    origin_facility = st.sidebar.selectbox("Select Origin Facility", facility_names)
    destination_facility = st.sidebar.selectbox("Select Destination Facility", facility_names)

    if origin_facility and destination_facility:
        try:
            st.subheader(f"Route from {origin_facility} to {destination_facility}")

            # Load the road network for Nairobi from OpenStreetMap
            G = load_road_network('Nairobi, Kenya')

            # Convert the coordinates to the nearest nodes in the graph
            orig_node = ox.distance.nearest_nodes(G, gdf.loc[gdf['facility_name'] == origin_facility, 'latitude'].values[0], 
                                                  gdf.loc[gdf['facility_name'] == origin_facility, 'longitude'].values[0])
            dest_node = ox.distance.nearest_nodes(G, gdf.loc[gdf['facility_name'] == destination_facility, 'latitude'].values[0], 
                                                  gdf.loc[gdf['facility_name'] == destination_facility, 'longitude'].values[0])

            # Folium map for route analysis
            route_map = folium.Map(location=[gdf.loc[gdf['facility_name'] == origin_facility, 'latitude'].values[0], 
                                             gdf.loc[gdf['facility_name'] == origin_facility, 'longitude'].values[0]], zoom_start=12)

            # Plot route on the map
            route = nx.shortest_path(G, orig_node, dest_node, weight='length')
            plot_route_on_map(route_map, route, route_color='blue')

            # Display the map with the route
            folium_static(route_map)

        except nx.NetworkXNoPath:
            st.error("No route found between the selected facilities.")

# Closest Facility Analysis Layer
st.sidebar.title("Closest Facility Analysis")
closest_facility_analysis = st.sidebar.button("Perform Closest Facility Analysis")

if closest_facility_analysis and 'gdf' in locals():
    st.sidebar.subheader("Select a Facility for Closest Facility Analysis")
    facility_names = gdf['facility_name'].tolist()
    selected_facility = st.sidebar.selectbox("Select a Facility", facility_names)

    if selected_facility:
        try:
            st.subheader(f"Closest Facility to {selected_facility}")

            # Create a Folium map
            closest_facility_map = folium.Map(location=[gdf.loc[gdf['facility_name'] == selected_facility, 'latitude'].values[0], 
                                                        gdf.loc[gdf['facility_name'] == selected_facility, 'longitude'].values[0]], zoom_start=12)

            # Add markers for all facilities
            add_markers_to_map(closest_facility_map, gdf[['latitude', 'longitude']].values)

            # Add marker for the closest facility point
            add_markers_to_map(closest_facility_map, [[gdf.loc[gdf['facility_name'] == selected_facility, 'latitude'].values[0], 
                                                       gdf.loc[gdf['facility_name'] == selected_facility, 'longitude'].values[0]]], color='red')

            # Display the map with closest facility analysis
            folium_static(closest_facility_map)

        except IndexError:
            st.error("Facility not found.")

# Service Area Analysis Layer
st.sidebar.title("Service Area Analysis")
service_area_analysis = st.sidebar.button("Perform Service Area Analysis")

if service_area_analysis and 'gdf' in locals():
    st.sidebar.subheader("Select a Facility for Service Area Analysis")
    facility_names = gdf['facility_name'].tolist()
    selected_facility = st.sidebar.selectbox("Select a Facility", facility_names)

    if selected_facility:
        try:
            st.subheader(f"Service Area around {selected_facility}")

            # Create a Folium map
            service_area_map = folium.Map(location=[gdf.loc[gdf['facility_name'] == selected_facility, 'latitude'].values[0], 
                                                    gdf.loc[gdf['facility_name'] == selected_facility, 'longitude'].values[0]], zoom_start=12)

            # Add marker for the service area center
            add_markers_to_map(service_area_map, [[gdf.loc[gdf['facility_name'] == selected_facility, 'latitude'].values[0], 
                                                   gdf.loc[gdf['facility_name'] == selected_facility, 'longitude'].values[0]]], color='purple')

            # Display the map with service area analysis
            folium_static(service_area_map)

        except IndexError:
            st.error("Facility not found.")

# OD Cost Matrix Analysis Layer
st.sidebar.title("OD Cost Matrix Analysis")
od_cost_matrix_analysis = st.sidebar.button("Perform OD Cost Matrix Analysis")

if od_cost_matrix_analysis and 'gdf' in locals():
    st.sidebar.subheader("Select Origin and Destination Facilities for OD Cost Matrix Analysis")
    facility_names = gdf['facility_name'].tolist()
    origin_facility = st.sidebar.selectbox("Select Origin Facility", facility_names)
    destination_facilities = st.sidebar.multiselect("Select Destination Facilities", facility_names)

    if origin_facility and destination_facilities:
        try:
            st.subheader(f"OD Cost Matrix from {origin_facility} to {', '.join(destination_facilities)}")

           #create a folium map
            od_cost_matrix_map = folium.Map(location=[gdf.loc[gdf['facility_name'] == origin_facility, 'latitude'].values[0], 
                                                        gdf.loc[gdf['facility_name'] == origin_facility, 'longitude'].values[0]], zoom_start=8)

            # Plot markers for origin and destination facilities
            add_markers_to_map(od_cost_matrix_map, [[gdf.loc[gdf['facility_name'] == origin_facility, 'latitude'].values[0], 
                                                     gdf.loc[gdf['facility_name'] == origin_facility, 'longitude'].values[0]]], color='green')

            for dest_facility in destination_facilities:
                add_markers_to_map(od_cost_matrix_map, [[gdf.loc[gdf['facility_name'] == dest_facility, 'latitude'].values[0], 
                                                         gdf.loc[gdf['facility_name'] == dest_facility, 'longitude'].values[0]]], color='red')

                # Calculate and plot routes from origin to each destination facility
                orig_coords = (gdf.loc[gdf['facility_name'] == origin_facility, 'latitude'].values[0], 
                               gdf.loc[gdf['facility_name'] == origin_facility, 'longitude'].values[0])
                dest_coords = (gdf.loc[gdf['facility_name'] == dest_facility, 'latitude'].values[0], 
                               gdf.loc[gdf['facility_name'] == dest_facility, 'longitude'].values[0])
                route = ox.shortest_path(G, orig_coords, dest_coords, weight='length')
                plot_route_on_map(od_cost_matrix_map, route, route_color='blue')

            # Display the map with OD Cost Matrix analysis
            folium_static(od_cost_matrix_map)

        except IndexError:
            st.error("Facility not found.")

# Vehicle Routing Problem (VRP) Analysis Layer
st.sidebar.title("Vehicle Routing Problem (VRP) Analysis")
vrp_analysis = st.sidebar.button("Perform VRP Analysis")

if vrp_analysis and 'gdf' in locals():
    st.sidebar.subheader("Select Facilities for VRP Analysis")
    facility_names = gdf['facility_name'].tolist()
    selected_facilities = st.sidebar.multiselect("Select Facilities", facility_names)

    if selected_facilities:
        try:
            st.subheader("Vehicle Routing Problem Analysis")

            # Generate a list of coordinates for selected facilities
            facility_coords = [(gdf.loc[gdf['facility_name'] == facility, 'latitude'].values[0], 
                                gdf.loc[gdf['facility_name'] == facility, 'longitude'].values[0]) for facility in selected_facilities]

            # Create a Folium map centered around the mean coordinates of selected facilities
            vrp_map = folium.Map(location=[sum([coord[0] for coord in facility_coords])/len(facility_coords),
                                           sum([coord[1] for coord in facility_coords])/len(facility_coords)], zoom_start=8)

            # Add markers for selected facilities
            add_markers_to_map(vrp_map, facility_coords, color='green')

            # Display the map with VRP analysis
            folium_static(vrp_map)

        except IndexError:
            st.error("Facility not found.")

# Location-Allocation Analysis Layer
st.sidebar.title("Location-Allocation Analysis")
location_allocation_analysis = st.sidebar.button("Perform Location-Allocation Analysis")

if location_allocation_analysis and 'gdf' in locals():
    st.sidebar.subheader("Select Demand Points for Location-Allocation Analysis")
    facility_names = gdf['facility_name'].tolist()
    selected_facilities = st.sidebar.multiselect("Select Demand Points", facility_names)

    if selected_facilities:
        try:
            st.subheader("Location-Allocation Analysis")

            # Generate a list of coordinates for selected demand points
            demand_coords = [(gdf.loc[gdf['facility_name'] == facility, 'latitude'].values[0], 
                              gdf.loc[gdf['facility_name'] == facility, 'longitude'].values[0]) for facility in selected_facilities]

            # Create a Folium map centered around the mean coordinates of selected demand points
            location_allocation_map = folium.Map(location=[sum([coord[0] for coord in demand_coords])/len(demand_coords),
                                                           sum([coord[1] for coord in demand_coords])/len(demand_coords)], zoom_start=8)

            # Add markers for selected demand points
            add_markers_to_map(location_allocation_map, demand_coords, color='blue')

            # Display the map with Location-Allocation analysis
            folium_static(location_allocation_map)

        except IndexError:
            st.error("Demand point not found.")

# Example template for CSV upload
st.sidebar.markdown("""
### Example CSV Format
- OBJECTID,facility_name,Type,Owner,County,Sub_County,Division,Location,Sub_Locati,Constituen,Nearest_To,latitude,longitude
""")

# Example template for Shapefile upload
st.sidebar.markdown("""
### Example Shapefile Upload
- Upload all shapefile components (.shp, .shx, .dbf, .prj) together
""")

