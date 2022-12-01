import csv
import warnings
from io import StringIO
import pandas as pd
import PIL.Image as Image
import requests
import streamlit as st
import joblib
warnings.filterwarnings('ignore')



footer = """
<style>
footer:after {
    content : 'Created by: Awesome DSA GROUP, ';
    display: block;
    position: relative;
    padding: 5px 0px;
    top: 3px;
}
.block-container {
    padding: 1rem !important
}
</style>
"""
img = Image.open('Epita.png')
st.image(img, width=500)
st.markdown(footer, unsafe_allow_html=True)
st.title('Flight Price Prediction')
st.subheader('Enter the details of the flight to get the price')

with st.expander('On Demand Prediction'):
    # Getting input from the user
    input_dict = {
        'Airline': st.selectbox('Airline', ('Air_India', 'AirAsia', 'GO_FIRST', 'Indigo', 'SpiceJet', 'Vistara')),
        'Source_city': st.selectbox('Source City', ('Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai')),
        'Destination_city': st.selectbox('Destination City', ('Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai')),
        'Class': st.radio('Class', ('Business', 'Economy')),
        'Stops': st.radio('Stops', ('zero', 'one', 'two_or_more')),
        'Departure_time': st.selectbox('Departure Time', ('Early_Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late_Night')),
        'Arrival_time': st.selectbox('Arrival Time', ('Early_Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late_Night')),
        'Duration': st.number_input('Duration in hours', min_value=0, max_value=100, value=0),
        'Days_left': st.number_input('Days left for the flight', min_value=0, max_value=100, value=0)
    }

    # Displaying the input to the user
    st.write('The input given by the user is:')
    st.write(input_dict)


    if st.button('Predict'):
        response = requests.post('http://127.0.0.1:8000/predict', json=input_dict)
        prediction = (response.json())
        st.write('The price of the flight is: ', prediction['prediction'])


with st.expander('Batch Prediction'):
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['price']=''

    if st.button('Predict Batch'):

        for i in range(len(df)):
            input_dict = {
                'Airline': str(df['airline'][i]),
                'Source_city': str(df['source_city'][i]),
                'Destination_city': str(df['destination_city'][i]),
                'Class': str(df['class'][i]),
                'Stops': str(df['stops'][i]),
                'Departure_time': str(df['departure_time'][i]),
                'Arrival_time': str(df['arrival_time'][i]),
                'Duration': str(df['duration'][i]),
                'Days_left': str(df['days_left'][i])

            }
            response = requests.post('http://127.0.0.1:8000/predict', json=input_dict)
            prediction = (response.json())
            df['price'][i] = prediction['prediction']

        st.write(df)

with st.expander('Get Past Predictions'):
    n = st.number_input('Enter the number of past predictions you want to see', min_value=0, max_value=100, value=0)
    date1 = st.date_input('From')
    time1 = st.text_input('Enter the time in HH:MM format', '00:00')
    date2 = st.date_input('To')
    time2 = st.text_input('Enter the time in HH:MM format', '12:00')
  
    if st.button('Get Past Predictions'):
        response = requests.get('http://127.0.0.1:8000/pastpredictions', params={'n': n, 'date1': date1, 'time1': time1, 'date2': date2, 'time2': time2})
        #Converting it intp a dataframe
        data = response.json()
        df = pd.DataFrame(data)
        st.write(df)
