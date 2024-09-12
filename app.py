import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from functions import nearest_neighbor, total_distance, convert_distance, simulate_route

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




# Add navigation in the sidebar
page = st.sidebar.selectbox("Choose a page", ["Introduction", "Optimization"])

if 'page' not in st.session_state:
    st.session_state.page = "Introduction"  # Default to Introduction page

if page == "Introduction":
    # Introduction Page
    st.title("Welcome to the Delivery Route Optimization Project")

    # Adding an image to the introduction page
    # st.image("image.jpg", caption="Optimizing Delivery Routes", use_column_width=True)
    st.image("image.webp", caption="Optimizing Delivery Routes")


    st.write("""
        Welcome to this web application designed to demonstrate how delivery routes can be optimized 
        to ensure efficiency and reduce travel time. This project uses a nearest neighbor algorithm to 
        find the best route for a delivery vehicle visiting multiple locations within a specified region.

        ### Scope of the Project:
        In this application, you will:
        - **Generate random delivery locations within the city of London**: The system will randomly create delivery points for demonstration purposes.
        - **Optimize the delivery route**: Using the nearest neighbor algorithm, the app calculates the most efficient path for visiting all delivery locations.
        - **Visualize the optimized route** on an interactive map, allowing you to see the sequence in which the locations will be visited.
        - **Estimate total distance and time** required for the delivery: Once the route is optimized, you will get an estimated total distance traveled and the expected time to complete the delivery.

        ### Instructions for Using the App:
        1. **Start the Optimization Process**: After reviewing the project description, you can proceed to the route optimization page.
        2. **Generate Delivery Locations**: On the optimization page, the system will generate random delivery points within the bounds of London.
        3. **Optimize and Visualize the Route**: You can run the optimization algorithm and visualize the most efficient route on a map.
        4. **Review the Results**: The app will display the total distance and estimated time for the delivery, as well as simulate the delivery route on the map.

        ### How to Proceed:
        - To begin the optimization, **click on the dropdown menu at the top left of the page** and select the **"Optimization"** option. This will take you to the page where you can generate delivery locations and start the optimization process.
        """)

    



# optimisation page starts here        
else:
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

        # setting marker size
        df['MarkerSize'] = 0.9

        # Display the interactive map for generated locations
        fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", hover_data=["Latitude", "Longitude"], size='MarkerSize', zoom=8, color_discrete_sequence=['red'], title="Generated Locations")
        fig.update_layout(mapbox_style='open-street-map', margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig)

    # Add distance unit selection and average speed input for eta calculation
    distance_unit = st.sidebar.radio("Select Distance Unit", ("Kilometers", "Miles"))

    # Default speed based on unit selection
    if distance_unit == "Kilometers":
        default_speed = 30  # Default urban speed in km/h
    else:
        default_speed = 20  # Default urban speed in mph

    average_speed = st.sidebar.number_input(f"Average Speed ({'km/h' if distance_unit == 'Kilometers' else 'mph'})", min_value=1, max_value=100, value=default_speed)
    # Sidebar slider for simulation speed
    simulation_speed = st.sidebar.slider("Adjust Simulation Speed", min_value=1, max_value=10, value=5)


    if st.sidebar.button("Optimize and Simulate Route"):
        if st.session_state.locations.size > 0:
            locations = st.session_state.locations
            route, exec_time = nearest_neighbor(locations)  # Get the optimized route
            
            total_dist_km = total_distance(route, locations)

            # Convert distance based on user selection (Kilometers or Miles)
            total_dist = convert_distance(total_dist_km, distance_unit)

            # Calculate ETA (time = distance / speed)
            eta_hours = total_dist / average_speed
            eta_minutes = eta_hours * 60
            
            st.write("Simulating the delivery route...")
            simulate_route(route, locations, speed=simulation_speed)  
            # Prepare the essay-style text output for distance and travel time
            distance_unit_label = 'kilometers' if distance_unit == 'Kilometers' else 'miles'
            essay_text = f"The total distance to be covered on this delivery route is approximately {total_dist:.2f} {distance_unit_label}. " \
                        f"With an average speed of {average_speed:.2f} {distance_unit_label} per hour, " \
                        f"it is estimated that the entire journey will take around {eta_minutes:.0f} minutes, " \
                        f"which is approximately {eta_hours:.2f} hours. " \
                        f"The route has been optimized to minimize the total distance and maximize efficiency, " \
                        f"ensuring that all delivery points are visited in a timely manner."

            # Add a note about traffic conditions and constraints
            note = "\n\n**Note:** This estimation assumes ideal driving conditions and does not account for real-world variables " \
                "such as traffic delays, road closures, or other potential constraints that may affect the delivery time."

            # Combine the essay text and note
            full_text = essay_text + note

            # Display the text in Streamlit
            st.write(full_text)
            
        else:
            st.warning("Please generate locations first.")


