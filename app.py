import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

cities = pd.read_csv('./data/uscities.csv')

state_names = ['', 'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
       'Colorado', 'Connecticut', 'Delaware', 'District of Columbia',
       'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana',
       'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
       'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
       'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire',
       'New Jersey', 'New Mexico', 'New York', 'North Carolina',
       'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
       'Puerto Rico', 'Rhode Island', 'South Carolina', 'South Dakota',
       'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
       'West Virginia', 'Wisconsin', 'Wyoming']

def get_url_state(name):
    return '+'.join(name.split()).upper()

def get_distance(lat1, lng1, lat2, lng2):
    return np.sqrt((lat1 - lat2)**2 + (lng1 - lng2)**2)

def get_nearest_city(lat, lng, df=cities):
    closest_index = 0
    min_distance = 1000000
    for i, row in df.iterrows():
        distance = get_distance(lat, lng, row['lat'], row['lng'])
        if distance < min_distance:
            min_distance = distance
            closest_index = i
    return df.iloc[closest_index]

st.set_page_config()
st.title("Per Diem Finder")
st.write('''Please fill in the information below to obtain the per-diem rates. 
         Additionally, you may click the map to get per-diem rates for the nearest city to your mouse click!''')

city_name = ''

col1, col2 = st.columns(2)
with col1:
    state = st.selectbox('State', state_names, index=0)
    if state:
        url = f'https://www.defensetravel.dod.mil/pdcgi/pd-rates/cpdratesx4.cgi?state={get_url_state(state)}&year=24&elocs=YES&military=YES&submit1=CALCULATE'
        tables = pd.read_html(url)
        data = tables[2]

        header = data.iloc[0]
        data = data[1:]
        data.columns = header
        data.reset_index(drop=True, inplace=True)
        data = data.apply(pd.to_numeric, errors='ignore')
        city_list = list(data['LOCATION (1)'].sort_values().unique())
        city_list = [''] + city_list
if state:
    with col2:
        city_name = st.selectbox('City', city_list)

lat = 40
lng = -100

if city_name:
    try:
        selected = cities[(cities['state_name'] == state) & (cities['city'].str.upper() == city_name)]
        lat = selected['lat']
        lng = selected['lng']
        m = folium.Map(location=[lat, lng], zoom_start=10)
    except:
        st.error('Could not find that city in the database, more errors will follow!!!!!')

m = folium.Map(location=[lat, lng], zoom_start=10)

map_object = st_folium(m, width=700, height=400)

last_clicked = map_object['last_clicked']

if last_clicked:
    nearest_city = get_nearest_city(map_object['last_clicked']['lat'], map_object['last_clicked']['lng'])
    state = nearest_city['state_name']
    city_name = nearest_city['city']

    url = f'https://www.defensetravel.dod.mil/pdcgi/pd-rates/cpdratesx4.cgi?state={get_url_state(state)}&year=24&elocs=YES&military=YES&submit1=CALCULATE'

    tables = pd.read_html(url)
    data = tables[2]
    header = data.iloc[0]
    data = data[1:]
    data.columns = header
    data.reset_index(drop=True, inplace=True)
    data = data.apply(pd.to_numeric, errors='ignore')
    last_clicked = ''


if city_name:
    st.write(f'The per diem rates for {city_name}, {state.upper()} are:')
    data[data['LOCATION (1)'] == city_name.upper()][['LOCATION (1)', 'Seasons (Beg-End)', 'Max Lodging', 'Local  Meals', 'Proportional Meals', 'Incidentals', 'Maximum Per Diem']]
    city_name = ''

