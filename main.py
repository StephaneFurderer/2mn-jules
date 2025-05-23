
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time
import random

# Page configuration
st.set_page_config(
    page_title="Hurricane Tracker - East Coast US",
    page_icon="🌪️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffecb5;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Hurricane historical data (2019-2024, Category 3+ affecting NC/FL)
@st.cache_data
def load_historical_data():
    """Load historical hurricane data for NC and FL (Cat 3+, 2019-2024)"""
    historical_hurricanes = [
        # 2019
        {
            "name": "Dorian",
            "year": 2019,
            "category": 5,
            "max_wind_speed": 185,
            "landfall_date": "2019-09-06",
            "state": "North Carolina",
            "estimated_damage": 1.6,  # billion USD
            "path": [
                {"lat": 26.5, "lon": -76.8, "time": "2019-09-01 00:00", "wind": 185, "category": 5},
                {"lat": 27.2, "lon": -78.2, "time": "2019-09-02 00:00", "wind": 175, "category": 5},
                {"lat": 28.5, "lon": -79.1, "time": "2019-09-03 00:00", "wind": 165, "category": 5},
                {"lat": 32.1, "lon": -79.8, "time": "2019-09-04 00:00", "wind": 145, "category": 4},
                {"lat": 34.2, "lon": -77.9, "time": "2019-09-05 00:00", "wind": 115, "category": 3},
                {"lat": 35.1, "lon": -75.7, "time": "2019-09-06 00:00", "wind": 105, "category": 2}
            ]
        },
        # 2020
        {
            "name": "Isaias",
            "year": 2020,
            "category": 3,
            "max_wind_speed": 115,
            "landfall_date": "2020-08-04",
            "state": "North Carolina",
            "estimated_damage": 4.8,
            "path": [
                {"lat": 25.8, "lon": -79.2, "time": "2020-08-01 00:00", "wind": 115, "category": 3},
                {"lat": 27.1, "lon": -80.1, "time": "2020-08-02 00:00", "wind": 105, "category": 2},
                {"lat": 32.4, "lon": -80.8, "time": "2020-08-03 00:00", "wind": 95, "category": 1},
                {"lat": 34.1, "lon": -78.2, "time": "2020-08-04 00:00", "wind": 85, "category": 1},
                {"lat": 36.2, "lon": -76.1, "time": "2020-08-04 12:00", "wind": 75, "category": 1}
            ]
        },
        # 2021
        {
            "name": "Elsa",
            "year": 2021,
            "category": 3,
            "max_wind_speed": 105,
            "landfall_date": "2021-07-07",
            "state": "Florida",
            "estimated_damage": 1.2,
            "path": [
                {"lat": 25.2, "lon": -82.1, "time": "2021-07-06 00:00", "wind": 105, "category": 3},
                {"lat": 26.8, "lon": -82.8, "time": "2021-07-07 00:00", "wind": 95, "category": 1},
                {"lat": 28.1, "lon": -82.4, "time": "2021-07-07 12:00", "wind": 85, "category": 1},
                {"lat": 30.4, "lon": -83.2, "time": "2021-07-08 00:00", "wind": 75, "category": 1}
            ]
        },
        # 2022
        {
            "name": "Ian",
            "year": 2022,
            "category": 4,
            "max_wind_speed": 150,
            "landfall_date": "2022-09-28",
            "state": "Florida",
            "estimated_damage": 112.9,
            "path": [
                {"lat": 24.1, "lon": -83.2, "time": "2022-09-26 00:00", "wind": 150, "category": 4},
                {"lat": 25.8, "lon": -82.1, "time": "2022-09-27 00:00", "wind": 145, "category": 4},
                {"lat": 26.6, "lon": -82.0, "time": "2022-09-28 00:00", "wind": 150, "category": 4},
                {"lat": 27.2, "lon": -81.8, "time": "2022-09-28 12:00", "wind": 125, "category": 3},
                {"lat": 28.4, "lon": -81.2, "time": "2022-09-29 00:00", "wind": 85, "category": 1}
            ]
        },
        # 2023
        {
            "name": "Idalia",
            "year": 2023,
            "category": 3,
            "max_wind_speed": 125,
            "landfall_date": "2023-08-30",
            "state": "Florida",
            "estimated_damage": 3.6,
            "path": [
                {"lat": 25.4, "lon": -84.2, "time": "2023-08-29 00:00", "wind": 125, "category": 3},
                {"lat": 27.1, "lon": -83.8, "time": "2023-08-30 00:00", "wind": 125, "category": 3},
                {"lat": 29.9, "lon": -83.4, "time": "2023-08-30 12:00", "wind": 105, "category": 2},
                {"lat": 31.2, "lon": -81.2, "time": "2023-08-31 00:00", "wind": 85, "category": 1}
            ]
        },
        # 2024
        {
            "name": "Helene",
            "year": 2024,
            "category": 4,
            "max_wind_speed": 140,
            "landfall_date": "2024-09-26",
            "state": "Florida",
            "estimated_damage": 47.8,
            "path": [
                {"lat": 25.1, "lon": -84.8, "time": "2024-09-25 00:00", "wind": 140, "category": 4},
                {"lat": 27.8, "lon": -84.2, "time": "2024-09-26 00:00", "wind": 140, "category": 4},
                {"lat": 30.4, "lon": -84.3, "time": "2024-09-26 12:00", "wind": 115, "category": 3},
                {"lat": 33.1, "lon": -83.8, "time": "2024-09-27 00:00", "wind": 95, "category": 1},
                {"lat": 35.2, "lon": -82.4, "time": "2024-09-27 12:00", "wind": 75, "category": 1}
            ]
        },
        {
            "name": "Milton",
            "year": 2024,
            "category": 5,
            "max_wind_speed": 180,
            "landfall_date": "2024-10-09",
            "state": "Florida",
            "estimated_damage": 85.0,
            "path": [
                {"lat": 25.8, "lon": -85.1, "time": "2024-10-08 00:00", "wind": 180, "category": 5},
                {"lat": 27.2, "lon": -82.8, "time": "2024-10-09 00:00", "wind": 165, "category": 5},
                {"lat": 27.8, "lon": -82.1, "time": "2024-10-09 12:00", "wind": 125, "category": 3},
                {"lat": 28.9, "lon": -81.2, "time": "2024-10-10 00:00", "wind": 85, "category": 1}
            ]
        }
    ]
    return historical_hurricanes

@st.cache_data(ttl=30)  # Cache for 30 seconds to simulate real-time updates
def simulate_active_storm():
    """Simulate an active storm for demo purposes"""
    base_time = datetime.now()
    
    # Create a simulated active storm path
    active_storm = {
        "name": "Demo Storm",
        "current_category": random.choice([3, 4, 5]),
        "current_wind_speed": random.randint(115, 175),
        "last_update": base_time.strftime("%Y-%m-%d %H:%M UTC"),
        "forecast_path": []
    }
    
    # Generate forecast positions (next 5 days)
    lat_start, lon_start = 24.5, -80.2
    for i in range(20):  # 20 points over 5 days
        hours_ahead = i * 6  # Every 6 hours
        future_time = base_time + timedelta(hours=hours_ahead)
        
        # Simulate northward movement with some randomness
        lat = lat_start + (i * 0.8) + random.uniform(-0.3, 0.3)
        lon = lon_start - (i * 0.2) + random.uniform(-0.2, 0.2)
        wind = max(75, active_storm["current_wind_speed"] - (i * 3) + random.randint(-10, 10))
        
        category = 5 if wind >= 157 else 4 if wind >= 130 else 3 if wind >= 111 else 2 if wind >= 96 else 1
        
        active_storm["forecast_path"].append({
            "lat": lat,
            "lon": lon,
            "time": future_time.strftime("%Y-%m-%d %H:%M"),
            "wind": wind,
            "category": category,
            "forecast_hour": hours_ahead
        })
    
    return active_storm

def get_category_color(category):
    """Return color based on hurricane category"""
    colors = {
        1: "#74add1",  # Light blue
        2: "#fee090",  # Yellow
        3: "#f46d43",  # Orange
        4: "#d73027",  # Red
        5: "#a50026"   # Dark red
    }
    return colors.get(category, "#808080")

def create_historical_map(hurricanes, selected_years, selected_names, selected_states):
    """Create interactive map showing historical hurricane paths"""
    fig = go.Figure()
    
    # Filter hurricanes based on selections
    filtered_hurricanes = []
    for hurricane in hurricanes:
        if (hurricane["year"] in selected_years and 
            hurricane["name"] in selected_names and 
            hurricane["state"] in selected_states):
            filtered_hurricanes.append(hurricane)
    
    # Add hurricane paths
    for hurricane in filtered_hurricanes:
        path_data = hurricane["path"]
        
        # Extract coordinates and categories
        lats = [point["lat"] for point in path_data]
        lons = [point["lon"] for point in path_data]
        categories = [point["category"] for point in path_data]
        winds = [point["wind"] for point in path_data]
        times = [point["time"] for point in path_data]
        
        # Add path line
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines+markers',
            line=dict(width=4, color=get_category_color(hurricane["category"])),
            marker=dict(
                size=8,
                color=[get_category_color(cat) for cat in categories],
                symbol="circle"
            ),
            name=f"{hurricane['name']} ({hurricane['year']})",
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Lat: %{lat:.2f}<br>"
                "Lon: %{lon:.2f}<br>"
                "Wind: %{customdata[0]} mph<br>"
                "Category: %{customdata[1]}<br>"
                "Time: %{customdata[2]}"
                "<extra></extra>"
            ),
            text=[f"{hurricane['name']} ({hurricane['year']})" for _ in lats],
            customdata=list(zip(winds, categories, times))
        ))
        
        # Add landfall marker
        landfall_point = path_data[-1]  # Last point as approximation
        fig.add_trace(go.Scattermapbox(
            lat=[landfall_point["lat"]],
            lon=[landfall_point["lon"]],
            mode='markers',
            marker=dict(
                size=15,
                color='red',
                symbol='star'
            ),
            name=f"{hurricane['name']} Landfall",
            hovertemplate=(
                f"<b>{hurricane['name']} Landfall</b><br>"
                f"Date: {hurricane['landfall_date']}<br>"
                f"Max Wind: {hurricane['max_wind_speed']} mph<br>"
                f"Category: {hurricane['category']}<br>"
                f"Damage: ${hurricane['estimated_damage']:.1f}B"
                "<extra></extra>"
            ),
            showlegend=False
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=30, lon=-80),
            zoom=5
        ),
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig

def create_realtime_map(active_storm):
    """Create map showing simulated real-time storm"""
    fig = go.Figure()
    
    if active_storm and active_storm["forecast_path"]:
        path_data = active_storm["forecast_path"]
        
        # Current position (first point)
        current = path_data[0]
        
        # Forecast path
        lats = [point["lat"] for point in path_data]
        lons = [point["lon"] for point in path_data]
        categories = [point["category"] for point in path_data]
        winds = [point["wind"] for point in path_data]
        times = [point["time"] for point in path_data]
        
        # Add forecast path
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lons,
            mode='lines+markers',
            line=dict(width=3, color='blue', dash='dash'),
            marker=dict(
                size=6,
                color=[get_category_color(cat) for cat in categories],
                opacity=0.7
            ),
            name="Forecast Path",
            hovertemplate=(
                "<b>Forecast Position</b><br>"
                "Time: %{customdata[0]}<br>"
                "Wind: %{customdata[1]} mph<br>"
                "Category: %{customdata[2]}<br>"
                "Hours ahead: %{customdata[3]}"
                "<extra></extra>"
            ),
            customdata=list(zip(times, winds, categories, [p["forecast_hour"] for p in path_data]))
        ))
        
        # Add current position
        fig.add_trace(go.Scattermapbox(
            lat=[current["lat"]],
            lon=[current["lon"]],
            mode='markers',
            marker=dict(
                size=20,
                color=get_category_color(current["category"]),
                symbol='circle',
                line=dict(width=3, color='white')
            ),
            name=f"Current Position",
            hovertemplate=(
                f"<b>{active_storm['name']}</b><br>"
                f"Current Wind: {active_storm['current_wind_speed']} mph<br>"
                f"Category: {active_storm['current_category']}<br>"
                f"Last Update: {active_storm['last_update']}"
                "<extra></extra>"
            )
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=28, lon=-82),
            zoom=6
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    return fig

def create_damage_chart(hurricanes, selected_years):
    """Create bar chart of hurricane damage by year"""
    # Filter and aggregate damage by year
    yearly_damage = {}
    for hurricane in hurricanes:
        if hurricane["year"] in selected_years:
            year = hurricane["year"]
            if year not in yearly_damage:
                yearly_damage[year] = 0
            yearly_damage[year] += hurricane["estimated_damage"]
    
    if not yearly_damage:
        return None
    
    fig = px.bar(
        x=list(yearly_damage.keys()),
        y=list(yearly_damage.values()),
        title="Total Hurricane Damage by Year (Billions USD)",
        labels={"x": "Year", "y": "Damage (Billions USD)"}
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title="Damage (Billions USD)"
    )
    
    return fig

# Main application
def main():
    # Header
    st.markdown('<h1 class="main-header">🌪️ Hurricane Tracker - East Coast US</h1>', unsafe_allow_html=True)
    
    # Load data
    hurricanes = load_historical_data()
    active_storm = simulate_active_storm()
    
    # Sidebar controls
    st.sidebar.header("📊 Filters")
    
    # Real-time toggle
    show_realtime = st.sidebar.checkbox("Show Simulated Real-Time Storm", value=True)
    
    if show_realtime:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔴 Live Storm Status")
        st.sidebar.metric(
            "Storm Name", 
            active_storm["name"],
            help="Simulated active storm for demonstration"
        )
        st.sidebar.metric(
            "Current Category", 
            active_storm["current_category"]
        )
        st.sidebar.metric(
            "Wind Speed", 
            f"{active_storm['current_wind_speed']} mph"
        )
        st.sidebar.text(f"Last Update: {active_storm['last_update']}")
        
        # Auto-refresh button
        if st.sidebar.button("🔄 Refresh Storm Data"):
            st.cache_data.clear()
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Historical Data Filters")
    
    # Historical filters
    available_years = sorted(list(set([h["year"] for h in hurricanes])))
    selected_years = st.sidebar.multiselect(
        "Select Years",
        available_years,
        default=available_years
    )
    
    available_names = sorted(list(set([h["name"] for h in hurricanes])))
    selected_names = st.sidebar.multiselect(
        "Select Hurricane Names",
        available_names,
        default=available_names
    )
    
    available_states = sorted(list(set([h["state"] for h in hurricanes])))
    selected_states = st.sidebar.multiselect(
        "Select States",
        available_states,
        default=available_states
    )
    
    # Main content area
    if show_realtime:
        st.subheader("🔴 Real-Time Storm Tracking")
        st.markdown(f"""
        <div class="warning-box">
            <strong>⚠️ Demo Mode:</strong> This shows a simulated active storm for demonstration. 
            In production, this would connect to real-time hurricane data feeds from NOAA/NWS.
        </div>
        """, unsafe_allow_html=True)
        
        # Real-time metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Storm Name", active_storm["name"])
        with col2:
            st.metric("Category", active_storm["current_category"])
        with col3:
            st.metric("Wind Speed", f"{active_storm['current_wind_speed']} mph")
        with col4:
            st.metric("Forecast Hours", "120")
        
        # Real-time map
        realtime_fig = create_realtime_map(active_storm)
        st.plotly_chart(realtime_fig, use_container_width=True)
    
    st.markdown("---")
    
    # Historical section
    st.subheader("📊 Historical Hurricane Analysis (2019-2024)")
    st.markdown("**Major hurricanes (Category 3+) that impacted North Carolina and Florida**")
    
    # Filter validation
    if not selected_years or not selected_names or not selected_states:
        st.warning("Please select at least one option from each filter to display historical data.")
        return
    
    # Historical map
    hist_fig = create_historical_map(hurricanes, selected_years, selected_names, selected_states)
    st.plotly_chart(hist_fig, use_container_width=True)
    
    # Summary statistics
    filtered_hurricanes = [
        h for h in hurricanes 
        if h["year"] in selected_years and h["name"] in selected_names and h["state"] in selected_states
    ]
    
    if filtered_hurricanes:
        col1, col2 = st.columns(2)
        
        with col1:
            # Hurricane summary table
            st.subheader("Hurricane Summary")
            summary_data = []
            for h in filtered_hurricanes:
                summary_data.append({
                    "Name": h["name"],
                    "Year": h["year"],
                    "Category": h["category"],
                    "Max Wind (mph)": h["max_wind_speed"],
                    "State": h["state"],
                    "Landfall Date": h["landfall_date"],
                    "Damage ($B)": f"${h['estimated_damage']:.1f}B"
                })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True)
        
        with col2:
            # Damage chart
            st.subheader("Economic Impact")
            damage_fig = create_damage_chart(hurricanes, selected_years)
            if damage_fig:
                st.plotly_chart(damage_fig, use_container_width=True)
            
            # Key statistics
            total_damage = sum([h["estimated_damage"] for h in filtered_hurricanes])
            avg_category = np.mean([h["category"] for h in filtered_hurricanes])
            max_wind = max([h["max_wind_speed"] for h in filtered_hurricanes])
            
            st.metric("Total Damage", f"${total_damage:.1f}B")
            st.metric("Average Category", f"{avg_category:.1f}")
            st.metric("Highest Wind Speed", f"{max_wind} mph")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Sources:** Historical hurricane data compiled from NOAA Hurricane Database (HURDAT2) and National Weather Service reports.
    Real-time simulation demonstrates potential integration with live weather APIs.
    
    **Note:** This is a demonstration application. For actual hurricane tracking, please refer to official sources like 
    the National Hurricane Center (nhc.noaa.gov) and National Weather Service.
    """)

if __name__ == "__main__":
    main()
