import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from datetime import datetime,timedelta

st.set_page_config(layout="wide")
sns.set_theme(style="white")

df = pd.read_csv("master_data.csv")
df["date"] = pd.to_datetime(df[["year","month","day","hour"]])


pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
station_data = df.groupby(['date', 'station'])[pollutants].mean().reset_index()
stations = station_data['station'].unique()

min_date = station_data['date'].min()
max_date = station_data['date'].max()
def convert_date(str_date):
  date_object = datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
  return date_object.strftime("%d %b %Y")

def create_line_chart_date_range(df_value,type):
  line_styles = ['-', '--', '-.', ':']
  colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown', 'pink', 'gray']
  fig, ax = plt.subplots(figsize =(19,6))
  for index,station in enumerate(stations):
    random_style = np.random.choice(line_styles)
    color = colors[index % len(colors)]
    station_value = df_value[df_value['station'] == station]
    ax.plot(station_value["date"], station_value[type], label=station,
            color=color, linestyle=random_style)

  ax.set_xlim([df_value['date'].min(), df_value['date'].max()])
  ax.set_title(f"Trend of Pollutant for the period {convert_date(str(df_value['date'].min()))} - {convert_date(str(df_value['date'].max()))} on {type}")
  ax.set_ylabel('Concentration (µg/m³)')
  ax.legend()
  ax.grid(axis='y', linestyle='--', color='gray')
  plt.xticks(rotation = 45)
  st.pyplot(fig)

def create_map_distribution(df_value,type):
  st.header(f"{type} Index Heatmap by Station Location")
  m = folium.Map(location=[39.9042, 116.4074], zoom_start=10) #lokasi beijing
  heat_data = [[data['Latitude'], data['Longitude'], data[type]] for index,data in df_value.iterrows()]
  HeatMap(heat_data).add_to(m)
  st_folium(m,use_container_width=True)


with st.sidebar:
  st.subheader("Air Quality")
  st.image("air_quality_logo.png", width=200)

  start_date,end_date = st.date_input("Select Date Range",value=[min_date,max_date],max_value=max_date,min_value=min_date)
  end_date += timedelta(days=1)

main_df = df[(df["date"] >= str(start_date)) & 
              (df["date"] <= str(end_date))
              ]

st.header("Air Quality Index (AQI) Beijing,China")
  
selected_polutant = st.selectbox("Pollutants",pollutants)

create_line_chart_date_range(main_df,selected_polutant)

create_map_distribution(main_df,selected_polutant)