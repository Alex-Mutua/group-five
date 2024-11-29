
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
import plotly.express as px
import requests
import matplotlib.pyplot as plt
import numpy as np
import streamlit.components.v1 as components  # <-- Import components

# Function to style the app with a professional gradient background
def add_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(to right, #f8f9fa, #e9ecef); /* Subtle gray gradient */
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: #343a40; /* Dark gray text for readability */
        }
        h1, h2 {
            color: #007bff; /* Professional blue for headings */
            text-align: center;
        }
        h3 {
            color: #495057; /* Darker gray for subheadings */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

add_background()

# App Header
st.markdown("<h1>GROUP FIVE WEB SCRAPER APP</h1>", unsafe_allow_html=True)
st.markdown("""
In this app, we have designed it to perform webscraping of data from Expat-Dakar over multiple pages.
We can also download scraped data or view dashboards directly.
* **Python libraries:** streamlit, requests, BeautifulSoup, pandas, matplotlib
* **Data source:** [Expat-Dakar](https://www.expat-dakar.com/).
""")

st.markdown("""**GROUP MEMBERS**
1. Mutua Vundi Alex
2. Mariem Tidiani DIA
3. Thiemokho Fall
""")

# Function to cache and convert DataFrame to CSV
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

# Function to load and display data in the app
def load(dataframe, title, key, key1):
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
    if st.button(title, key1):
        st.subheader('Data Dimension')
        st.write(f'{dataframe.shape[0]} rows, {dataframe.shape[1]} columns')
        st.dataframe(dataframe)

        csv = convert_df(dataframe)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f'{title.replace(" ", "_")}.csv',
            mime='text/csv',
            key=key
        )

# Function for web scraping
def load_apartment_data(url_template, page):
    url = url_template.format(page=page)
    res = requests.get(url)
    soup = bs(res.text, 'html.parser')
    containers = soup.find_all("div", class_="listings-cards__list-item")

    data = []
    for container in containers:
        try:
            link = container.find('a')['href']
            res_c = requests.get(link)
            soup_c = bs(res_c.text, 'html.parser')

            details = soup_c.find('div', class_="listing-item__details").text.split()[6]
            area = soup_c.find("dd", class_="listing-item__properties__description").text.strip().replace("m²", "")
            address = soup_c.find("div", class_="listing-item__address").text.strip()
            price = soup_c.find("span", class_="listing-card__price__value").text.strip().replace("\u202f", "").replace("F Cfa", "")
            image_link = soup_c.find("div", class_="gallery__image__inner").img["srcset"]

            data.append({
                'Details': details,
                'Area': area,
                'Address': address,
                'Price': price,
                'ImageLink': image_link
            })
        except:
            pass
            
    return pd.DataFrame(data)

# Sidebar for user input
st.sidebar.markdown("<h1 style='color: white;'>The User Input Features</h1>", unsafe_allow_html=True)

# Category selector
category = st.sidebar.selectbox(
    'Select Category',
    ['Rental Apartment', 'Furnished Apartments', 'Land For Sale']
)

# Set page range based on the category
if category == 'Rental Apartment':
    page_range = range(1, 124)  # Pages 1 to 123
elif category == 'Furnished Apartments':
    page_range = range(1, 79)  # Pages 1 to 78
else:
    page_range = range(1, 50)  # Pages 1 to 49 for Land For Sale

Pages = st.sidebar.selectbox('Page Index', list(page_range))

# User action selector
Choices = st.sidebar.selectbox(
    'Options',
    ['Scrape the data using BeautifulSoup', 'Download the scraped data', 'Dashboard of the data(clean)', 'Please fill the app form']
)

# setting argument of the project
if Choices == 'Scrape the data using BeautifulSoup':
    if category == 'Rental Apartment':
        with st.spinner('Scraping Rental Apartment data, please wait...'):
            data = load_apartment_data('https://www.expat-dakar.com/appartements-a-louer?page={page}', Pages)
            load(data, 'Rental Apartment', '1', '101')
    elif category == 'Furnished Apartments':
        with st.spinner('Scraping Furnished Apartments data, please wait...'):
            data = load_apartment_data('https://www.expat-dakar.com/appartements-meubles?page={page}', Pages)
            load(data, 'Furnished Apartments', '2', '102')
    else:  # Land For Sale
        with st.spinner('Scraping Land For Sale data, please wait...'):
            data = load_apartment_data('https://www.expat-dakar.com/terrains-a-vendre?page={page}', Pages)
            load(data, 'Land For Sale', '3', '103')

elif Choices == 'Download the scraped data':
    if category == 'Rental Apartment':
        
            data = pd.read_csv('Apartment_1.csv')
            load(data, 'Rental Apartment', '1', '101')
            st.error('Data for Rental Apartment not found!')
    elif category == 'Furnished Apartments':
        
            data = pd.read_csv('Apartment_2.csv')
            load(data, 'Furnished Apartments', '2', '102')
    else:  # Land For Sale
        
            data = pd.read_csv('Apartment_3.csv')
            load(data, 'Land For Sale', '3', '103')

elif Choices == 'Dashboard of the data(clean)':

        if category == 'Rental Apartment':
            df = pd.read_csv('Url1.csv')
        elif category == 'Furnished Apartments':
            df = pd.read_csv('Url2.csv')
        else:  # Land For Sale
            df = pd.read_csv('Url3.csv')

        st.subheader(f'Dashboard for {category}')
        
        # Price Distribution
        fig = px.histogram(df, x="Price", nbins=50, title=f'Price Distribution for {category}')
        st.plotly_chart(fig)

        # Top Areas Pie Chart
        fig = px.pie(df, names='Area', title=f'Top Areas for {category}', hole=0.3)
        st.plotly_chart(fig)

else:
    # Embed the form
    st.markdown("<h3>Please fill the Form Below</h3>", unsafe_allow_html=True)
    components.html(
        """
        <iframe src="https://ee.kobotoolbox.org/x/lgUh1tWb" width="800" height="1100"></iframe>
        """,
        height=1100,
        width=800,
    )