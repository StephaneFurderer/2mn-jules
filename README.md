# Major Hurricane Trajectory Visualizer

This Streamlit application visualizes historical trajectories of major hurricanes (Category 3 and above) from the past 10 years that impacted North Carolina and/or Florida.

## Features

*   Interactive map displaying storm paths.
*   Filters for Year, Hurricane Name, and Affected Region (North Carolina, Florida).
*   Display of key hurricane metadata: Name, Max Category, Max Wind Speed, Earliest Recorded Date (UTC), and Landfall States.

## Data Format (`hurricanes.csv`)

The application expects a CSV file named `hurricanes.csv` in the same directory as `app.py`. The CSV file must contain the following columns:

*   `point_id`: A unique identifier for each data point/track segment (text/string).
*   `storm_id`: A unique identifier for each hurricane (text/string, e.g., "ALPHA2015"). All points for the same storm share the same `storm_id`.
*   `name`: The name of the hurricane (text/string, e.g., "Alpha").
*   `date`: The date of the record in `YYYYMMDD` format (integer or text).
*   `time`: The time of the record in `HHMM` UTC format (integer or text, e.g., 1200 for 12:00 PM UTC).
*   `latitude`: Latitude of the hurricane center (float, e.g., 25.5).
*   `longitude`: Longitude of the hurricane center (float, e.g., -79.0).
*   `max_wind_speed_mph`: Maximum sustained wind speed in miles per hour (integer).
*   `min_pressure_mb`: Minimum central pressure in millibars (integer).
*   `category`: Hurricane category (integer, 1-5). The application filters for 3 and above.
*   `landfall_states`: A string indicating US states of landfall, separated by commas if multiple (e.g., "FL", "NC", "FL,NC"). The application filters for states containing "FL" or "NC".

A sample `hurricanes.csv` is provided with a few examples.

## Setup Instructions

1.  **Clone the repository or download the files.**
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    Ensure you have `requirements.txt` in the same directory.
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  Ensure `hurricanes.csv` is in the root directory alongside `app.py`.
2.  Run the Streamlit application using the following command:
    ```bash
    streamlit run app.py
    ```
    The application should open in your web browser.

## Dependencies

*   Streamlit
*   Pandas
*   Numpy
