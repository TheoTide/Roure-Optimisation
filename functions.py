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