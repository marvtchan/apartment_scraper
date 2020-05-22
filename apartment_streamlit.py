# apartment_streamlit.py

import streamlit as st
from streamlit import caching

import sqlite3  
from sqlalchemy import create_engine, select, MetaData, Table, Integer, String, inspect, Column, ForeignKey
import os

import datetime as dt
from datetime import datetime
from datetime import timedelta
import dateutil.relativedelta

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pydeck as pdk



def main():
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Analysis", "Visualize Map"])

    if page == "Homepage":
        st.title("Apartment Searcher")
        st.markdown(
        """
   			This is an exploratory page for searching an apartment in the Bay Area.

        """)
        st.subheader("Analysis")
        st.markdown(
        """
        We can analyze the apartment market here
        """)
        st.sidebar.text(" ")
        st.sidebar.text(" ")
        st.sidebar.text(" ")
        st.sidebar.success('Explore the datasets with the \'Analysis\' page or visualize the listing with the \'Visualize Map\' page.')
    elif page == "Analysis":
        caching.clear_cache()
        data = load_data()
        st.title("📈Analysis📉")
        st.markdown(
        """
        The analysis below shows a bar chart of monthly transaction data aggregated by categories.

        To analyze:

           1. Navigate to sidebar for options.

           2. Select date range and categories for monthly analysis. 

           3. Check filtered data and raw data for deeper insight.

           4. Expense is negative while income is positive.

        """)
        if st.checkbox("Display total data", False):
        	st.subheader("Raw Data")
        	st.write(data)
    elif page == "Visualize Map":
        df = load_data()
        st.title("Apartments in the Area")
        st.markdown(
        """
        We can visualize apartments on a map here.

        """)
        selected_filtered_data, location = filter_data(df)
        map(df, selected_filtered_data, location)


@st.cache(persist=True)
def load_data():
	engine = create_engine('sqlite:////Users/marvinchan/Documents/PythonProgramming/apartment_scraper/apartments.db', echo=False)
	connection = engine.raw_connection()
	cursor = connection.cursor()
	data = pd.read_sql_query('SELECT * FROM listings', connection)
	return data

def filter_data(data):
    location = st.multiselect("Enter Location", sorted(data['location'].unique()))
    print(location)
    selected_filtered_data = data[(data['location'].isin(location))]
    return selected_filtered_data, location

def map(df, filtered, location):
	midpoint = (np.average(df['lat']), np.average(df['lon']))
	layer= pdk.Layer(
		'ScatterplotLayer',
		data=filtered,
		get_position='[lon, lat]',
		auto_highlight=True,
		pickable=True,
		radiusScale= 120,
		radiusMinPixels= 5,
		getFillColor= [248, 24, 148],
	)

	view_state=pdk.ViewState(
		latitude=midpoint[0],
		longitude=midpoint[1],
		zoom=4
	)

	r = pdk.Deck(
		map_style='mapbox://styles/mapbox/light-v9',
		layers=[layer],
		initial_view_state=view_state,
		tooltip={'html': '<b>Price:</b> {price}', 'style': {'color': 'white'}},
	)
	st.pydeck_chart(r)

	location_data_is_check = st.checkbox("Display the data of selected locations")

	if location_data_is_check:
		st.subheader("Filtered data by for '%s" % (location))
		st.write(df)

	if st.checkbox("Display total data", False):
		st.subheader("Raw data")
		st.write(df)

if __name__ == "__main__":
    main()
