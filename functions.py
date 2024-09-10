import numpy as np
from math import radians, sin, cos, sqrt, atan2
import time
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st
 
#  Haversine function to calculate distance between two points
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat/2) * sin(d_lat/2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon/2) * sin(d_lon/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c  # Distance in km
    return distance

# Function to calculate total distance of a route
def total_distance(route, locations):
    distance = 0
    for i in range(len(route) - 1):
        distance += haversine(locations[route[i]][0], locations[route[i]][1], locations[route[i+1]][0], locations[route[i+1]][1])
    return distance

# Function to calculate adaptability to constraints
def adaptability_to_constraints(route, delivery_windows):
    for i in range(len(route) - 1):
        if not (delivery_windows[route[i]][0] <= delivery_windows[route[i+1]][0] <= delivery_windows[route[i]][1]):
            return False
    return True

# Function to display metrics
def display_metrics(locations, delivery_windows):
    route, exec_time = nearest_neighbor(locations)
    total_dist = total_distance(route, locations)
    adapt_constraints = adaptability_to_constraints(route, delivery_windows)
    num_routes = 1  # Assuming single vehicle for simplicity

    print(f"Total Distance: {total_dist} km")
    print(f"Execution Time: {exec_time} seconds")
    print(f"Adaptability to Constraints: {'Yes' if adapt_constraints else 'No'}")
    print(f"Number of Routes/Trips: {num_routes}")
    return route


def plot_route(locations, route):
    # Extract the route coordinates
    lats = [locations[i][0] for i in route]
    lons = [locations[i][1] for i in route]

    # Create a scatter plot for the locations
    fig, ax = plt.subplots()
    ax.scatter(lons, lats, color='red', marker='o', s=100, label='Locations')

    # Plot lines connecting the route
    for i in range(len(route) - 1):
        ax.plot([lons[route[i]], lons[route[i+1]]], 
                [lats[route[i]], lats[route[i+1]]], 
                color='blue', linestyle='-', linewidth=2)

    # Connect the last point to the first point to complete the route
    ax.plot([lons[route[-1]], lons[route[0]]], 
            [lats[route[-1]], lats[route[0]]], 
            color='blue', linestyle='-', linewidth=2)

    # Annotate each point with its route number from the route variable
    for i, index in enumerate(route):
        lat = lats[i]
        lon = lons[i]
        ax.text(lon, lat, f'{index}', fontsize=12, ha='center', color='black', bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    # Label and title
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('Optimized Delivery Route')
    ax.legend()

    # Display the plot in Streamlit
    st.pyplot(fig)
    
    print(index)



# define the Nearest Neighbor function
# Nearest Neighbor algorithm to create a sample route
def nearest_neighbor(locations):
    start_time = time.time()
    unvisited = list(range(1, len(locations)))
    route = [0]
    while unvisited:
        nearest = min(unvisited, key=lambda x: haversine(locations[route[-1]][0], locations[route[-1]][1], locations[x][0], locations[x][1]))
        route.append(nearest)
        unvisited.remove(nearest)
    route.append(0)
    execution_time = time.time() - start_time
    return route, execution_time

# Function to convert distance based on the selected unit
def convert_distance(distance_km, unit):
    if unit == "Miles":
        return distance_km * 0.621371  # Convert km to miles
    return distance_km

# Simulation function to simulate the optimized route with markers at each delivery point
def simulate_route(route, locations, speed=5):
    """Simulate the movement of the vehicle along the delivery route, with markers at each delivery point."""
    fig = go.Figure()
    
    # Initialize the first marker (start point)
    current_lat, current_lon = locations[route[0]]

    # Plot the starting point (Start marker)
    fig.add_trace(go.Scattermapbox(
        lat=[current_lat],
        lon=[current_lon],
        mode='markers+text',
        marker=dict(size=12, color='green', symbol='star'),
        text=['Start'],
        textposition='top right'
    ))

    # Plot all delivery points as static markers
    for idx, location_index in enumerate(route):
        lat, lon = locations[location_index]
        fig.add_trace(go.Scattermapbox(
            lat=[lat],
            lon=[lon],
            mode='markers+text',
            marker=dict(size=10, color='orange', symbol='circle'),
            text=[f'Delivery {idx+1}'],
            textposition='top right'
        ))

    # Configure the map layout (static parts)
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=np.mean(locations[:, 0]), lon=np.mean(locations[:, 1])),
            zoom=8,
        ),
        margin=dict(t=0, b=0, l=0, r=0)
    )

    # Display the initial figure
    map_plot = st.plotly_chart(fig, use_container_width=True)

    # Iterate through the route to simulate vehicle movement
    for i in range(1, len(route)):
        # Get the current and next locations
        current_index = route[i - 1]
        next_index = route[i]
        
        start_lat, start_lon = locations[current_index]
        end_lat, end_lon = locations[next_index]

        # Simulate moving from start to end by interpolating between points
        num_steps = 20  # Number of steps for the animation
        lat_steps = np.linspace(start_lat, end_lat, num_steps)
        lon_steps = np.linspace(start_lon, end_lon, num_steps)

        # Simulate movement by updating the marker's position at each step
        for j in range(num_steps):
            fig.data = []  # Clear previous markers

            # Plot the current position of the moving vehicle
            fig.add_trace(go.Scattermapbox(
                lat=[lat_steps[j]],
                lon=[lon_steps[j]],
                mode='markers',
                marker=dict(size=12, color='blue', symbol='circle'),
                text=[f'Location {i+1}'],
                textposition='top right'
            ))

            # Plot the static delivery points again to keep them visible
            for idx, location_index in enumerate(route):
                lat, lon = locations[location_index]
                fig.add_trace(go.Scattermapbox(
                    lat=[lat],
                    lon=[lon],
                    mode='markers+text',
                    marker=dict(size=10, color='orange', symbol='circle'),
                    text=[f'Delivery {idx+1}'],
                    textposition='top right'
                ))

            # Plot the line representing the full route
            route_lats = [locations[idx][0] for idx in route[:i+1]]
            route_lons = [locations[idx][1] for idx in route[:i+1]]
            
            fig.add_trace(go.Scattermapbox(
                lat=route_lats + [lat_steps[j]],
                lon=route_lons + [lon_steps[j]],
                mode='lines',
                line=dict(width=2, color='blue'),
            ))

            # Update the map plot with the new marker position
            map_plot.plotly_chart(fig, use_container_width=True)

            # Pause between steps to create the animation effect (speed control)
            time.sleep(0.1 / speed)

    # After the loop, mark the final location (End marker)
    end_lat, end_lon = locations[route[-1]]
    fig.add_trace(go.Scattermapbox(
        lat=[end_lat],
        lon=[end_lon],
        mode='markers+text',
        marker=dict(size=12, color='red', symbol='square'),
        text=['End'],
        textposition='top right'
    ))

    # Display the final figure with all delivery points and the end point
    map_plot.plotly_chart(fig, use_container_width=True)
