import numpy as np
from math import radians, sin, cos, sqrt, atan2
import time
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
 
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

# # Simulation function to simulate the optimized route with markers at each delivery point
# def simulate_route(route, locations, speed=5):
#     """Simulate the movement of the vehicle along the delivery route, with markers at each delivery point."""
#     fig = go.Figure()
    
#     # Plot all delivery points as static markers
#     for idx, location_index in enumerate(route):
#         lat, lon = locations[location_index]
#         fig.add_trace(go.Scattermapbox(
#             lat=[lat],
#             lon=[lon],
#             mode='markers+text',
#             marker=dict(size=10, color='orange', symbol='circle'),
#             text=[f'Delivery {idx+1}'],
#             textposition='top right'
#         ))

#     # Plot the full route as a static line
#     route_lats = [locations[idx][0] for idx in route]
#     route_lons = [locations[idx][1] for idx in route]
#     fig.add_trace(go.Scattermapbox(
#         lat=route_lats,
#         lon=route_lons,
#         mode='lines',
#         line=dict(width=2, color='blue'),
#     ))

#     # Configure the map layout (static parts)
#     fig.update_layout(
#         mapbox=dict(
#             style="open-street-map",
#             center=dict(lat=np.mean(locations[:, 0]), lon=np.mean(locations[:, 1])),
#             zoom=8,
#         ),
#         margin=dict(t=0, b=0, l=0, r=0)
#     )

#     # Display the initial figure with static elements
#     map_plot = st.plotly_chart(fig, use_container_width=True)

#     # Add a dynamic marker for vehicle movement
#     vehicle_marker = go.Scattermapbox(
#         lat=[locations[route[0]][0]],
#         lon=[locations[route[0]][1]],
#         mode='markers',
#         marker=dict(size=12, color='blue', symbol='circle'),
#         text=['Start'],
#         textposition='top right'
#     )
#     fig.add_trace(vehicle_marker)

#     # Iterate through the route to simulate vehicle movement
#     for i in range(1, len(route)):
#         # Get the current and next locations
#         current_index = route[i - 1]
#         next_index = route[i]
        
#         start_lat, start_lon = locations[current_index]
#         end_lat, end_lon = locations[next_index]

#         # Simulate moving from start to end by interpolating between points
#         num_steps = 3  # Number of steps for the animation
#         lat_steps = np.linspace(start_lat, end_lat, num_steps)
#         lon_steps = np.linspace(start_lon, end_lon, num_steps)

#         # Simulate movement by updating the vehicle marker's position at each step
#         for j in range(num_steps):
#             # Update the vehicle marker with the new position
#             vehicle_marker.lat = [lat_steps[j]]
#             vehicle_marker.lon = [lon_steps[j]]

#             # Update the map plot with the new vehicle marker position
#             map_plot.plotly_chart(fig, use_container_width=True)

#             # Pause between steps to create the animation effect (speed control)
#             time.sleep(0.1 / speed)

#     # After the loop, update the final location of the vehicle marker
#     vehicle_marker.lat = [locations[route[-1]][0]]
#     vehicle_marker.lon = [locations[route[-1]][1]]
#     vehicle_marker.marker = dict(size=12, color='red', symbol='square')
#     vehicle_marker.text = ['End']

#     # Update the map with the final marker position
#     map_plot.plotly_chart(fig, use_container_width=True)



def simulate_route(optimized_route, locations, speed=500):
    """
    Simulates a route on a map and visualizes it using Plotly.

    Parameters:
    optimized_route (list): A list of indices representing the optimized route.
    locations (numpy array): An array of [latitude, longitude] coordinates.
    speed (int, optional): The duration of each frame in milliseconds. Default is 500ms.
    """
    speed = (10 - speed) * 100
    # Create a DataFrame with city names and coordinates
    city_route = [f"Location {i}" for i in optimized_route]
    lon_lat = locations[optimized_route]

    # Creating DataFrame
    df = pd.DataFrame({
        'city': city_route,
        'lon': lon_lat[:, 1],
        'lat': lon_lat[:, 0]
    })

    # Copy the existing DataFrame
    data = df.copy()

    # Add 'id' column for reference
    data['id'] = range(len(data))

    # Add 'color' column
    data['color'] = ""

    # Setting 'red' color for the first row (index 0) and 'black' for others
    data.loc[data['id'] == 0, 'color'] = 'red'
    data.loc[data['id'] != 0, 'color'] = 'black'

    # Get the start location
    start = data[data["id"] == 0][["lon", "lat"]].values[0]

    # Animated map visualization
    fig_2 = go.Figure()

    # Plot the entire route as a background trace (non-animated)
    fig_2.add_trace(go.Scattermapbox(
        lon=data['lon'],
        lat=data['lat'],
        mode='lines+markers',
        marker=dict(size=15, color='black'),
        line=dict(width=2, color='gray'),
        name='Route'
    ))

    # Create frames for animation (one point at a time)
    frames = []
    for i in range(len(data)):
        frames.append(go.Frame(
            data=[go.Scattermapbox(
                lon=data['lon'][:i+1],  # Plot points up to the current frame
                lat=data['lat'][:i+1],
                mode='lines+markers',
                marker=dict(size=15, color='red'),
                line=dict(width=3, color='red'),
                name='Moving'
            )],
            name=f'frame{i}'
        ))

    # Add frames to the figure
    fig_2.frames = frames

    # Set up the map style, zoom, and center
    fig_2.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=9,
            center=dict(lat=start[1], lon=start[0])
        ),
        width=1000,  # Width of the map
        height=750,  # Height of the map
        margin={"r":0,"t":0,"l":0,"b":0},
        updatemenus=[dict(type="buttons",
                          showactive=False,
                          buttons=[dict(label="Play",
                                        method="animate",
                                        args=[None, {"frame": {"duration": speed, "redraw": True},
                                                     "fromcurrent": True, "mode": "immediate"}]),
                                   dict(label="Pause",
                                        method="animate",
                                        args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                       "mode": "immediate"}])])])

    # Render the animated map figure in Streamlit
    st.plotly_chart(fig_2)
