import streamlit as st
import streamlit.components.v1 as components

# Title and description
st.title("3D Buildings and Terrain Visualization")
st.write("This application visualizes 3D buildings and terrain in Nairobi, Kenya using MapLibre GL JS and MapTiler.")

# Add a selection box to choose the layer to display
layer_option = st.selectbox(
    "Select layer to display:",
    ("3D Buildings", "3D Terrain", "Both")
)

# HTML code for MapLibre GL JS with 3D terrain and buildings
map_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>3D Buildings and Terrain Visualization</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <style>
        body {{ margin: 0; padding: 0; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; height: 100vh; }}
    </style>
    <link href="https://unpkg.com/maplibre-gl@1.15.2/dist/maplibre-gl.css" rel="stylesheet" />
    <script src="https://unpkg.com/maplibre-gl@1.15.2/dist/maplibre-gl.js"></script>
</head>
<body>
    <div id="map"></div>
    <script>
        const map = new maplibregl.Map({{
            container: 'map',
            style: 'https://api.maptiler.com/maps/streets/style.json?key=2C5GJFj20cu6dg83k0jU',
            center: [36.817223, -1.286389],
            zoom: 15,
            pitch: 60,
            bearing: -17.6,
            antialias: true
        }});

        map.on('load', () => {{
            {"map.addSource('terrain', { type: 'raster-dem', url: 'https://api.maptiler.com/tiles/terrain-rgb/tiles.json?key=2C5GJFj20cu6dg83k0jU', tileSize: 256, maxzoom: 14 }); map.setTerrain({source: 'terrain', exaggeration: 1.5}); map.addLayer({ 'id': 'sky', 'type': 'sky', 'paint': { 'sky-type': 'atmosphere', 'sky-atmosphere-sun': [0.0, 0.0], 'sky-atmosphere-sun-intensity': 15 } });" if layer_option in ["3D Terrain", "Both"] else ""}
            
            {"map.addSource('openmaptiles', { type: 'vector', url: 'https://api.maptiler.com/tiles/v3/tiles.json?key=2C5GJFj20cu6dg83k0jU' }); map.addLayer({ 'id': '3d-buildings', 'source': 'openmaptiles', 'source-layer': 'building', 'filter': ['==', '$type', 'Polygon'], 'type': 'fill-extrusion', 'minzoom': 15, 'paint': { 'fill-extrusion-color': '#aaa', 'fill-extrusion-height': [ 'interpolate', ['linear'], ['zoom'], 15, 0, 15.05, ['get', 'render_height'] ], 'fill-extrusion-base': [ 'interpolate', ['linear'], ['zoom'], 15, 0, 15.05, ['get', 'render_min_height'] ], 'fill-extrusion-opacity': 0.6 } });" if layer_option in ["3D Buildings", "Both"] else ""}
        }});
    </script>
</body>
</html>
"""

# Display the HTML file within the Streamlit app
components.html(map_html, height=600)
