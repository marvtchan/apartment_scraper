# apartment_streamlit.py
# streamlit
import streamlit as st
from streamlit import caching

#database
import sqlite3  
from sqlalchemy import create_engine, select, MetaData, Table, Integer, String, inspect, Column, ForeignKey
import os

#datetime
import datetime as dt
from datetime import datetime
from datetime import timedelta
import dateutil.relativedelta

#analysis and visualization
import pandas as pd
import numpy as np
from numpy import median, average
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import pydeck as pdk
import altair as alt
alt.data_transformers.disable_max_rows()



def main():
	### Allows user to switch between pages ###
    page = st.sidebar.selectbox("Choose a page", ["Homepage", "Analysis", "Visualize Map"])

    if page == "Homepage":
        st.title("Apartment Searcher")
        st.markdown(
        """
   			This is an exploratory page for searching an apartment in the Bay Area.
        """)
        st.markdown(
        """
            The data presented is scraped from craigslist and filtered for prices between $1,000 and $3,000. 
        """)
        st.markdown(
        """
            The area is East Bay.  
        """)
        st.subheader("Analyze")
        st.markdown(
        """
        We can analyze the apartment market on the 'Analysis' page.
        """)
        st.subheader("Visualize")
        st.markdown(
        """
        Proceed to the Visualize Map page to filter for apartments by location.
        """)
        st.markdown(
        """
        Below is a map of all available craigslist housing options:
        """)
        df = load_data()
        map(df, df)
        st.sidebar.text(" ")
        st.sidebar.text(" ")
        st.sidebar.text(" ")
        st.sidebar.success('Explore the datasets with the \'Analysis\' page or visualize the listing with the \'Visualize Map\' page.')
    elif page == "Analysis":
        data = load_data()
        st.title("📈Analysis📉")
        st.markdown(
        """
        The analysis below shows a bar chart of monthly transaction data aggregated by categories.

        To analyze:

           1. Navigate below for options.

           2. Select location and bedroom for binned scatter plot analysis. 

           3. Choose average, median, count and bedrooms for bar plot analysis.

           4. Check filtered data and raw data for deeper insight.

        """)
        
        selected_filtered_data, location, bedroom = filter_data(data)
        binned_scatter(selected_filtered_data)
        if st.checkbox("Display filtered data", False):
            st.subheader("Filtered Data")
            st.write(selected_filtered_data)


        selected_bedrooms, bedroom  = filter_bedrooms(data)

        bar_chart = st.selectbox("Choose an estimator", ["Average", "Median", "Count"])

        if bar_chart == "Average":
            try:
                average_bar(selected_bedrooms, average)
            except ValueError:
                pass

        elif bar_chart == "Median":
            try:
                average_bar(selected_bedrooms, median)
            except  ValueError:
                pass

        elif bar_chart == "Count":
            try:
                count_bar(selected_bedrooms)
            except ValueError:
                pass

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
        selected_filtered_data, location, bedroom = filter_data(df)

        map(df, selected_filtered_data)

        all_locations(df)

        show_data(df, selected_filtered_data, location, bedroom)

        show_listing(df)


# Load Data from database
@st.cache(persist=True)
def load_data():
    engine = create_engine('sqlite:////Users/marvinchan/Documents/PythonProgramming/apartment_scraper/apartments.db', echo=False)
    connection = engine.raw_connection()
    cursor = connection.cursor()
    data = pd.read_sql_query('SELECT * FROM listing', connection)
    data['bedrooms'] = data['bedrooms'].astype(str).replace("0.0", "Studio/Bedroom")
    data['bedrooms'] = data['bedrooms'].str.replace(".0", "")
    return data


# Filter data with location
def filter_data(data):
    location = st.multiselect("Enter Location", sorted(data['city'].unique()))
    bedroom = st.multiselect("Enter Bedrooms", sorted(data['bedrooms'].unique()))
    selected_filtered_data = data[(data['city'].isin(location))&(data['bedrooms'].isin(bedroom))]
    return selected_filtered_data, location, bedroom

# Visualize all data points on map
def map(df, filtered):
	midpoint = (np.average(df['lat']), np.average(df['lon']))
	layer= pdk.Layer(
		'ScatterplotLayer',
		data=filtered,
		get_position='[lon, lat]',
		auto_highlight=True,
		pickable=True,
		radiusScale= 80,
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
		tooltip={'html': '<b>ID:</b> {id} <br><b>Price:</b> {price} <br><b>Rooms:</b> {bedrooms}', 'style': {'color': 'white'}},
	)
	st.pydeck_chart(r)

# Button to show map with all locations
def all_locations(df):
	if st.button("Show all locations"):
        	map(df, df)

# Function to show data
def show_data(df, filtered, location, bedroom):
	location_data_is_check = st.checkbox("Display the data of selected locations")

	if location_data_is_check:
		st.subheader("Filtered data by for '%s & '%s rooms" % (location, bedroom))
		st.write(filtered)

	if st.checkbox("Display total data", False):
		st.subheader("Raw data")
		st.write(df)

def show_listing(df):
    index = st.text_input("Enter ID")
    if st.button("Show Listing"):
        try:
            st.write(df.ix[int(index) - 1])
        except (ValueError, KeyError):
            st.error('Inputted ID does not exist.')

def binned_scatter(df):
    source = df
    chart = alt.Chart(source).mark_circle().properties(
    width = 700,
    height = 500,
    ).encode(
        alt.X('bedrooms', bin=True),
        alt.Y('price', bin=True),
        size='count()',
        color='city',
        tooltip=['city', 'price', 'bedrooms']
    ).interactive()
    st.altair_chart(chart)

def filter_bedrooms(data):
    bedroom = st.multiselect("Enter bedrooms for bar chart", sorted(data['bedrooms'].unique()))
    selected_filtered_data = data[(data['bedrooms'].isin(bedroom))]
    return selected_filtered_data, bedroom

def average_bar(data, estimator):
    plt.figure(figsize=(8,5))
    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light', fontsize='medium')
    plt.tight_layout()
    ax = sns.barplot(x="city", y="price", data=data, estimator=estimator)    
    st.pyplot()

def count_bar(data):
    plt.figure(figsize=(8,5))
    plt.xticks(rotation=45, horizontalalignment='right', fontweight='light', fontsize='medium')
    plt.tight_layout()
    ax = sns.countplot(x='city', data=data)
    st.pyplot()

if __name__ == "__main__":
    main()
