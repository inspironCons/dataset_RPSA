import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
import random
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
sns.set_theme(style="white")

# Load data
df = pd.read_csv("https://raw.githubusercontent.com/inspironCons/dataset_RPSA/refs/heads/main/dashboard/master_data.csv")
df["date"] = pd.to_datetime(df[["year", "month", "day", "hour"]])

# Constants
POLLUTANTS = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
station_data = df.groupby(['date', 'station'])
stations = station_data['station'].unique()

min_date = station_data['date'].min()
max_date = station_data['date'].max()

# helper function to categorize the time of day 
def categorize_time_of_day(hour):
    if 0 <= hour <= 10:
        return 'Pagi'
    elif 10 < hour <= 14:
        return 'Siang'
    elif 14 < hour <= 18:
        return 'Sore'
    else:
        return 'Malam'

# Helper function to format date
def convert_date(str_date):
    date_object = datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
    return date_object.strftime("%d %b %Y")

# Line chart creation
def create_line_chart_date_range(df_value, pollutant_type,selected_statsiun):
    line_styles = random.choice(['-', '--', '-.', ':'])
    colors = random.choice(['b', 'g', 'r', 'c', 'm', 'y', 'k'])
    fig, ax = plt.subplots(figsize=(19, 6))
    
    ax.plot(df_value["date"], df_value[pollutant_type], label=selected_statsiun, color=colors, linestyle=line_styles)

    ax.set_xlim([df_value['date'].min(), df_value['date'].max()])
    ax.set_title(f"Trend of Pollutant for {convert_date(str(df_value['date'].min()))} - {convert_date(str(df_value['date'].max()))} on {pollutant_type}")
    ax.set_ylabel('Concentration (µg/m³)')
    ax.legend()
    ax.grid(axis='y', linestyle='-', color='gray')
    plt.xticks(rotation=45)
    st.pyplot(fig)

def create_chart_trend_based_time_of_day(df,type):
    most_polluted_by_time = df.groupby(['Time_of_Day'])[type].max()

# Map distribution creation
def create_map_distribution(df_value, pollutant_type):
    st.header(f"{pollutant_type} Index Heatmap by Station Location")
    
    if "Latitude" in df_value.columns and "Longitude" in df_value.columns:
        m = folium.Map(location=[df_value['Latitude'].mean(), df_value['Longitude'].mean()], zoom_start=10)
        heat_data = [[row['Latitude'], row['Longitude'], row[pollutant_type]] for _, row in df_value.iterrows()]
        HeatMap(heat_data).add_to(m)
        st_folium(m, use_container_width=True)
    else:
        st.error("Latitude and Longitude data not available for map generation.")

# Sidebar for user input
with st.sidebar:
    st.subheader("Air Quality")
    st.image("./dashboard/air_quality_logo.png", width=200)

    start_date, end_date = st.date_input("Select Date Range", value=[min_date, max_date], max_value=max_date, min_value=min_date)
    selected_statsiun = st.selectbox("Select station",stations)
    
    if start_date > end_date:
        st.error("Start date cannot be greater than end date.")
    else:
        end_date += timedelta(days=1)

# Filter dataset based on date input
main_df = df[(df["date"] >= str(start_date)) & (df["date"] <= str(end_date)) & (df["station"] == selected_statsiun)]

# Main content
st.header("Air Quality Index (AQI) Beijing, China")
selected_pollutant = st.selectbox("Pollutants", POLLUTANTS)

create_line_chart_date_range(main_df, selected_pollutant,selected_statsiun)
create_map_distribution(main_df, selected_pollutant)
