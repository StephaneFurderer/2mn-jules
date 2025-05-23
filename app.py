import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration (must be the first Streamlit command)
st.set_page_config(layout="wide", page_title="Major Hurricane Visualizer", page_icon="🌀")

st.title("Major Hurricane Trajectory Visualizer")
st.markdown("""
This application visualizes historical trajectories of major hurricanes (Category 3 and above) 
from the past 10 years that impacted North Carolina and/or Florida. 
Use the filters in the sidebar to explore the data.
""")

# Data loading and preprocessing will be added here
def load_data():
    """
    Reads hurricanes.csv, creates a timestamp_utc column, 
    and handles file not found errors.
    """
    try:
        df = pd.read_csv("hurricanes.csv")
        # Combine date and time into a single datetime column
        # Assuming date is YYYYMMDD and time is HHMM
        df['timestamp_utc'] = pd.to_datetime(df['date'].astype(str) + df['time'].astype(str).str.zfill(4), format='%Y%m%d%H%M', errors='coerce')
        return df
    except FileNotFoundError:
        st.error("Error: `hurricanes.csv` not found. Please make sure the file is in the correct directory.")
        return pd.DataFrame()

# Load and preprocess data
raw_df = load_data()

# Expander for data loading details - placed here so raw_df is in scope
data_details_expander = st.expander("Data Loading & Filtering Details", expanded=False)

if not raw_df.empty:
    with data_details_expander:
        st.write(f"Raw data rows: {len(raw_df)}")

    # Year Filtering: Last 10 full calendar years
    current_year = datetime.now().year
    start_year = current_year - 10
    end_year = current_year - 1 
    # Inclusive start, exclusive end for pd.Timestamp
    start_date = pd.Timestamp(f"{start_year}-01-01")
    end_date = pd.Timestamp(f"{end_year+1}-01-01") # up to Jan 1st of the current year, so includes all of end_year
    
    base_filtered_df = raw_df[
        (raw_df['timestamp_utc'] >= start_date) & 
        (raw_df['timestamp_utc'] < end_date)
    ].copy() # Use .copy() to avoid SettingWithCopyWarning

    # Category Filtering: category >= 3
    base_filtered_df = base_filtered_df[base_filtered_df['category'] >= 3]

    # Region Filtering: landfall_states contains "FL" or "NC"
    base_filtered_df = base_filtered_df[
        base_filtered_df['landfall_states'].str.contains("FL", na=False) | 
        base_filtered_df['landfall_states'].str.contains("NC", na=False)
    ]
    
    with data_details_expander:
        st.write(f"Rows after initial processing (last 10 yrs, Cat 3+, FL/NC): {len(base_filtered_df)}")
else:
    with data_details_expander:
        st.write("No data loaded, skipping processing.")
    base_filtered_df = pd.DataFrame() # Ensure base_filtered_df exists

# Filtering widgets will be added here
display_df = base_filtered_df.copy() # This will be further filtered by sidebar options

st.sidebar.header("Filters")
st.sidebar.caption("Adjust filters to update the map and data.")

if not base_filtered_df.empty:
    # Year Filter
    unique_years = sorted(base_filtered_df['timestamp_utc'].dt.year.unique())
    selected_years = st.sidebar.multiselect("Year", unique_years, default=unique_years)

    # Hurricane Name Filter
    unique_names = sorted(base_filtered_df['name'].unique())
    selected_names = st.sidebar.multiselect("Hurricane Name", unique_names, default=unique_names)

    # Affected Region Filter
    region_options = {"Florida": "FL", "North Carolina": "NC"}
    selected_regions_display = st.sidebar.multiselect("Affected Region", list(region_options.keys()), default=list(region_options.keys()))
    selected_region_codes = [region_options[region] for region in selected_regions_display]

    # Apply filters
    if selected_years and selected_years != unique_years: # Filter only if selection is made and not all are selected
        display_df = display_df[display_df['timestamp_utc'].dt.year.isin(selected_years)]
    
    if selected_names and selected_names != unique_names: # Filter only if selection is made and not all are selected
        display_df = display_df[display_df['name'].isin(selected_names)]

    if selected_region_codes and len(selected_region_codes) < len(region_options): # Filter only if selection is made and not all are selected
        # Ensure 'landfall_states' is string type to prevent .str accessor errors
        display_df['landfall_states'] = display_df['landfall_states'].astype(str)
        is_in_selected_region = display_df['landfall_states'].apply(
            lambda x: any(region_code in x for region_code in selected_region_codes)
        )
        display_df = display_df[is_in_selected_region]
    
    with data_details_expander: # Add current display_df count to expander
        st.write(f"Rows after interactive sidebar filters: {len(display_df)}")

else:
    st.sidebar.info("No data available to filter.")
    display_df = pd.DataFrame() # Ensure display_df is an empty DF if base_filtered_df is empty

# Map display will be added here
st.subheader("Hurricane Tracks Map")
if not display_df.empty and 'latitude' in display_df.columns and 'longitude' in display_df.columns:
    # Ensure latitude and longitude are numeric and handle any potential errors
    display_df['latitude'] = pd.to_numeric(display_df['latitude'], errors='coerce')
    display_df['longitude'] = pd.to_numeric(display_df['longitude'], errors='coerce')
    
    # Drop rows with NaN latitude or longitude that might have been coerced
    map_df = display_df.dropna(subset=['latitude', 'longitude'])
    
    if not map_df.empty:
        st.map(map_df)
        st.caption("Displaying all track points for filtered hurricanes. Each point represents a recorded location and time for a hurricane.")
    else:
        st.info("No valid geographic data (latitude, longitude) to display on the map for the selected hurricanes.")
elif not display_df.empty: # Renamed from processed_df to display_df
    st.warning("Processed data is available, but 'latitude' or 'longitude' columns are missing. Cannot display map.")
else:
    st.info("No hurricane data to display on the map based on current filters.")

# Metadata display will be added here
st.subheader("Filtered Hurricane Details")
if not display_df.empty:
    # Aggregate data per storm
    # Ensure 'storm_id' exists before grouping
    if 'storm_id' in display_df.columns:
        summary_df = display_df.groupby('storm_id').agg(
            name=('name', 'first'),
            max_category=('category', 'max'),
            max_wind_speed_mph=('max_wind_speed_mph', 'max'),
            earliest_timestamp_utc=('timestamp_utc', 'min'),
            landfall_states=('landfall_states', 'first')
        ).reset_index() # to make storm_id a column again

        # Rename columns for presentation
        summary_df.rename(columns={
            'name': 'Name',
            'max_category': 'Max Category',
            'max_wind_speed_mph': 'Max Wind Speed (mph)',
            'earliest_timestamp_utc': 'Earliest Record Date (UTC)',
            'landfall_states': 'Landfall States',
            'storm_id': 'Storm ID' # Optional: display storm_id as well
        }, inplace=True)
        
        # Reorder columns for display (optional, but good for presentation)
        # If storm_id is not needed in the final table, it can be removed from this list
        cols_to_display = ['Name', 'Storm ID', 'Max Category', 'Max Wind Speed (mph)', 'Earliest Record Date (UTC)', 'Landfall States']
        # Filter out any columns that might be missing if 'storm_id' wasn't in display_df for some reason (though it should be)
        cols_to_display = [col for col in cols_to_display if col in summary_df.columns]

        st.dataframe(summary_df[cols_to_display], use_container_width=True)
    else:
        st.warning("Cannot generate summary: 'storm_id' column is missing from the filtered data.")
else:
    st.info("No hurricane metadata to display based on current filters.")
