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
sns.set_theme(style="white",color_codes=True)

@st.cache_data
def load_data():
    return pd.read_csv("master_data.csv")

# Menentukan kategori waktu
def categorize_time(hour):
    if 0 <= hour < 6:
        return 'Pagi'
    elif 6 <= hour < 12:
        return 'Siang'
    elif 12 <= hour < 18:
        return 'Sore'
    else:
        return 'Malam'
    
df = load_data()
df["date"] = pd.to_datetime(df[["year","month","day","hour"]])
df['Time_Category'] = df['hour'].apply(categorize_time)


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
  random_style = np.random.choice(line_styles)
  color = np.random.choice(colors)
  ax.plot(df_value["date"], df_value[type], label=type, color=color, linestyle=random_style)
    
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

  heat_data = [[data['Latitude'], data['Longitude'], data[type]] for _,data in df_value.iterrows()]
  HeatMap(heat_data).add_to(m)
  st_folium(m,use_container_width=True)



def create_top_trend_pollutant(df_value,type):
  search_max_by_category_per_station = df_value.groupby(["Time_Category"])[type].max().reset_index()
  search_min_by_category_per_station = df_value.groupby(["Time_Category"])[type].min().reset_index()
  join_df_max = pd.merge(search_max_by_category_per_station,df_value,how="left",on=["Time_Category",type]).drop_duplicates(subset="Time_Category")
  join_df_min = pd.merge(search_min_by_category_per_station,df_value,how="left",on=["Time_Category",type]).drop_duplicates(subset="Time_Category")
  # buat chart
  fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(19, 6))
  barplot_max = sns.barplot(x=type, y="Time_Category", data=join_df_max, ax=ax[0])
  barplot_max.bar_label(barplot_max.containers[0], fontsize=10, label_type='center',labels=join_df_max["station"])
  barplot_max.bar_label(barplot_max.containers[0], fontsize=10, label_type='edge')

  
  ax[0].set_ylabel(None)
  ax[0].set_title(f"Worst Indexing Pollutan {type}",loc="center",fontsize=14)
  ax[0].set_xlabel("µg/m³")
  

  barplot_min = sns.barplot(x=type, y="Time_Category",hue_order="station", data=join_df_min, ax=ax[1])
  barplot_min.bar_label(barplot_min.containers[0], fontsize=10, label_type='center',labels=join_df_max["station"])
  barplot_min.bar_label(barplot_min.containers[0], fontsize=10, label_type='edge')
  ax[1].set_ylabel(None)
  ax[1].set_title(f"Best Indexing Pollutan {type}")
  ax[1].set_xlabel("µg/m³")
  
  st.pyplot(fig)


with st.sidebar:
  st.subheader("Air Quality")
  st.image("./dashboard/air_quality_logo.png", width=200)

  start_date,end_date = st.date_input("Select Date Range",value=[min_date,max_date],max_value=max_date,min_value=min_date)
  selected_station = st.selectbox("Select Station",stations)
  end_date += timedelta(days=1)

main_df = df[(df["date"] >= str(start_date)) & 
              (df["date"] <= str(end_date)) &
              (df["station"] == str(selected_station))
            ]

main_all_statsiun = df[(df["date"] >= str(start_date)) & 
              (df["date"] <= str(end_date))
            ]


st.header("Air Quality Index (AQI) Beijing,China")
col1,col2 = st.columns(2)

with col1:
  st.metric("Statsiun",selected_station)
with col2:  
  selected_polutant = st.selectbox("Pollutants",pollutants)


create_line_chart_date_range(main_df,selected_polutant)

create_top_trend_pollutant(main_all_statsiun,selected_polutant)

create_map_distribution(main_all_statsiun,selected_polutant)
