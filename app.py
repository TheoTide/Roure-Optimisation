import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from functions import nearest_neighbor, total_distance 

# Set page configuration
st.set_page_config(page_title="Delivery Route Optimization", page_icon="🚚", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    /* Style the sidebar */
    .sidebar .sidebar-content {
        background-color: #f0f0f5;
        padding: 20px;
        border-radius: 10px;
    }

    /* Style for title and headers */
    h1 {
        color: #4B8BBE;
        font-family: 'Arial', sans-serif;
    }

    h2 {
        color: #306998;
        font-family: 'Arial', sans-serif;
    }

    /* Style the dataframe */
    .dataframe {
        font-family: 'Arial', sans-serif;
        font-size: 15px;
    }

    /* Mapbox plot margin */
    .plotly-graph-div {
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* Center alignment for plots and texts */
    .centered {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    /* Style the main page background */
    .stApp {
        background-color: #f0f7ff;
        padding: 10px;
    }

    /* Add padding to buttons */
    .stButton>button {
        background-color: #4B8BBE;
        color: white;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
        margin-top: 10px;
    }

    /* Add padding to dataframes */
    .stDataFrame {
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* Style the text in sidebar */
    .sidebar .sidebar-text {
        font-size: 16px;
        font-family: 'Arial', sans-serif;
    }

    /* Footer styling */
    footer {
        visibility: hidden;
    }
    footer:after {
        content: 'Delivery Route Optimization - Created with 💙 by Your Name';
        visibility: visible;
        display: block;
        text-align: center;
        font-size: 14px;
        color: #306998;
        padding: 5px;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Title of the app
st.title("Delivery Route Optimization Software")

# Sidebar for user inputs
st.sidebar.header("User Input Parameters")

# Example input for delivery locations
num_locations = st.sidebar.number_input("Number of Delivery Locations", min_value=1, max_value=100, value=5)

# Initialize session state attributes if they don't exist
if 'locations' not in st.session_state:
    st.session_state.locations = np.empty((0, 2))

# Option to generate random delivery locations
if st.sidebar.button("Generate Locations"):
    # Define bounds for Central London area
    min_lat, max_lat = 51.3, 51.7  # Latitude bounds
    min_lon, max_lon = -0.2, 0.2  # Longitude bounds
    
    # Generate random latitude and longitude points within the specified bounds
    latitudes = np.random.uniform(min_lat, max_lat, num_locations)
    longitudes = np.random.uniform(min_lon, max_lon, num_locations)
    
    locations = np.column_stack((latitudes, longitudes))
    st.session_state.locations = locations

    st.success(f"{num_locations} locations generated within the London area!")

# Display the generated locations and plot
if st.session_state.locations.size > 0:
    df = pd.DataFrame(st.session_state.locations, columns=["Latitude", "Longitude"])
    
    # Display the generated locations
    st.write("Generated Delivery Locations:")
    st.dataframe(df)

    # Display the interactive map for generated locations
    fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", hover_data=["Latitude", "Longitude"], zoom=8, color_discrete_sequence=['red'], title="Generated Locations")
    fig.update_layout(mapbox_style='open-street-map', margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig)

# Button to run the optimization algorithm
if st.sidebar.button("Optimize Route"):
    if st.session_state.locations.size > 0:
        locations = st.session_state.locations

        # Run the nearest neighbor algorithm
        route, exec_time = nearest_neighbor(locations)
        total_dist = total_distance(route, locations)

        # Display the optimized route and metrics
        st.write("Optimized Route:")
        st.dataframe(pd.DataFrame(route, columns=["Route Order"]))

        st.write(f"Total Distance: {total_dist:.2f} km")
        st.write(f"Execution Time: {exec_time:.2f} seconds")

        # Plot the optimized route using Plotly
        fig = go.Figure()

        # Add scatter plot for locations
        fig.add_trace(go.Scattermapbox(
            lat=locations[:, 0],
            lon=locations[:, 1],
            mode='markers+text',
            marker=dict(size=10, color='red'),
            text=[f'Location {i+1}' for i in range(len(locations))],
            textposition='top right'
        ))

        # Add lines for the route
        route_lats = [locations[i][0] for i in route]
        route_lons = [locations[i][1] for i in route]
        route_lats.append(route_lats[0])  # To close the loop
        route_lons.append(route_lons[0])  # To close the loop
        
        fig.add_trace(go.Scattermapbox(
            lat=route_lats,
            lon=route_lons,
            mode='lines+markers',
            line=dict(width=2, color='blue'),
            marker=dict(size=8, color='green'),
            text=[f'Location {i+1}' for i in route] + [f'Location {route[0]+1}']
        ))

        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center=dict(lat=np.mean(locations[:, 0]), lon=np.mean(locations[:, 1])),
                zoom=8
            ),
            margin=dict(t=0, b=0, l=0, r=0)
        )

        st.plotly_chart(fig)
    else:
        st.warning("Please generate locations first.")
