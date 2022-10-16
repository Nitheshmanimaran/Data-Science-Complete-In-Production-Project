import base64
from ctypes.wintypes import SIZE
from io import StringIO
import streamlit as st
import pandas as pd 
import numpy as np
import datetime
import time
import emoji
import warnings
import csv
import PIL.Image as Image
import requests


warnings.filterwarnings('ignore')

img = Image.open('Epita.png')
st.image(img, width=500)

# Title
st.title('Flight Price Prediction')

# Streamlit subheader
st.subheader('Enter the details of the flight')

# Getting the input from the user for airline, source_city, destination_city, class, stops, departure_time, arrival_time, duration,days_left
airline = st.selectbox('Airline', ('Air_India', 'AirAsia', 'GO_FIRST', 'Indigo', 'SpiceJet', 'Vistara'))
source_city = st.selectbox('Source City', ('Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai'))
destination_city = st.selectbox('Destination City', ('Bangalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai'))

# Radio button for class
class_ = st.radio('Class', ('Business', 'Economy'))

# Radio button for stops
stops = st.radio('Stops', ('zero', 'one', 'two_or_more'))

# Selectbox for departure time
departure_time = st.selectbox('Departure Time', ('Early_Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late_Night'))

# Selectbox for arrival time
arrival_time = st.selectbox('Arrival Time', ('Early_Morning', 'Morning', 'Afternoon', 'Evening', 'Night', 'Late_Night'))

# Input for duration Saying user to enter the duration in hours
duration = st.number_input('Duration in hours', min_value=0, max_value=100, value=0)

# Input for days left
days_left = st.number_input('Days left for the flight', min_value=0, max_value=100, value=0)

# Creating a dataframe
df = pd.DataFrame({'Airline': [airline], 'Source_city': [source_city], 'Destination_city': [destination_city], 'Class': [class_], 'Stops': [stops], 'Departure_time': [departure_time], 'Arrival_time': [arrival_time], 'Duration': [duration], 'Days_left': [days_left]})

# Converting the categorical variables to numerical variables
df['Airline'] = df['Airline'].map({'Air_India': 0, 'AirAsia': 1, 'GO_FIRST': 2, 'Indigo': 3, 'SpiceJet': 4, 'Vistara': 5})
df['Source_city'] = df['Source_city'].map({'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5})
df['Destination_city'] = df['Destination_city'].map({'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5})
df['Class'] = df['Class'].map({'Business': 0, 'Economy': 1})
df['Stops'] = df['Stops'].map({'zero': 0, 'one': 1, 'two_or_more': 2})
df['Departure_time'] = df['Departure_time'].map({'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5})
df['Arrival_time'] = df['Arrival_time'].map({'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5})


# Displaying the dataframe
st.write(df)
# Convert the dataframe to a JSON string
json_data = {
    'Airline': str(df['Airline'].values[0]),
    'Source_city': str(df['Source_city'].values[0]),
    'Destination_city': str(df['Destination_city'].values[0]),
    'Class': str(df['Class'].values[0]),
    'Stops': str(df['Stops'].values[0]),
    'Departure_time': str(df['Departure_time'].values[0]),
    'Arrival_time': str(df['Arrival_time'].values[0]),
    'Duration': str(df['Duration'].values[0]),
    'Days_left': str(df['Days_left'].values[0])
}

# Send a POST request to the API
if st.button('Predict'):
    # Send the JSON to the API
    response = requests.post('http://127.0.0.1:8000/predict', json=json_data)
    # Get the prediction
    prediction = response.json()
    # Display the prediction
    st.write('The predicted price of the flight is', prediction['prediction'])

# Dropdown for batch prediction
batch_prediction = st.selectbox('Batch Prediction', ('Processed CSV', 'Unprocessed CSV'))

def processed_csv():
    uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)

    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)
    
    # Converting the bytes data to csv file
        csv_file = StringIO(bytes_data.decode('utf-8'))
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        column_names=[]
        row_values=[]
        for row in csv_reader:
            if line_count == 0:
            #Storing the column names in column_names
                column_names = row
                line_count += 1
            else:
            #Storing all the rows in row_values
                row_values.append(row)
                line_count += 1
        st.write(f'Processed {line_count - 1} lines.')

   
    # Displaying a table using the column names and row values
        df = pd.DataFrame(row_values, columns=column_names)
        st.write(df)
    
    # For batch prediction
        if st.button('Predict_Batch_Processed'):
            price = []
            for i in df.index:

                json_data = {
                    'Airline': str(df['airline'].values[i]),
                    'Source_city': str(df['source_city'].values[i]),
                    'Destination_city': str(df['destination_city'].values[i]),
                    'Class': str(df['class'].values[i]),
                    'Stops': str(df['stops'].values[i]),
                    'Departure_time': str(df['departure_time'].values[i]),
                    'Arrival_time': str(df['arrival_time'].values[i]),
                    'Duration': str(df['duration'].values[i]),
                    'Days_left': str(df['days_left'].values[i])
                }
                response = requests.post('http://127.0.0.1:8000/predict', json=json_data)
                prediction = response.json()
                
                #st.write('The predicted price of the flight is', prediction['prediction'])
                price.append(prediction['prediction'])
            df['Price'] = price

            st.write('The dataframe with the predicted price is')
            st.write(df)

def unprocessed_csv():


    uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)

    for uploaded_file in uploaded_files:
        bytes_data = uploaded_file.read()
        st.write("filename:", uploaded_file.name)
    
    # Converting the bytes data to csv file
        csv_file = StringIO(bytes_data.decode('utf-8'))
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        column_names=[]
        row_values=[]
        for row in csv_reader:
            if line_count == 0:
            #Storing the column names in column_names
                column_names = row
                line_count += 1
            else:
            #Storing all the rows in row_values
                row_values.append(row)
                line_count += 1
        st.write(f'Processed {line_count - 1} lines.')

   
    # Displaying a table using the column names and row values
        df = pd.DataFrame(row_values, columns=column_names)
        #st.write(df)

    # deleting the unwanted columns from the dataframe - unnamed column with index, flight, price

        df = df.drop(['index', 'flight','price'], axis=1)
        #st.write(df)

        #Creating a dictionary for the airline column in alphabetical order
        airline_dict = {'Air_India': 0, 'AirAsia': 1, 'GO_FIRST': 2, 'Indigo': 3, 'SpiceJet': 4, 'Vistara': 5}
        #Creating a dictionary for the source_city column in alphabetical order
        source_city_dict = {'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5}
        #Creating a dictionary for the destination_city column in alphabetical order
        destination_city_dict = {'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5}
        #Creating a dictionary for the class column in alphabetical order
        class_dict = {'Business': 0, 'Economy': 1}
        #Creating a dictionary for the departure_time column in alphabetical order
        departure_time_dict = {'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5}
        #Creating a dictionary for the arrival_time column in alphabetical order
        arrival_time_dict = {'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5}
        #Creating a dictionary for the stops column in alphabetical order
        stops_dict = {'zero': 0, 'one': 1, 'two_or_more': 2}

        #Replacing the categorical values with the corresponding numerical values
        df['airline'] = df['airline'].map(airline_dict)
        df['source_city'] = df['source_city'].map(source_city_dict)
        df['destination_city'] = df['destination_city'].map(destination_city_dict)
        df['class'] = df['class'].map(class_dict)
        df['departure_time'] = df['departure_time'].map(departure_time_dict)
        df['arrival_time'] = df['arrival_time'].map(arrival_time_dict)
        df['stops'] = df['stops'].map(stops_dict)
        #Converting the duration column to integer
        df['duration'] = df['duration'].astype(float)
        df['duration'] = df['duration'].astype(int)
        df['days_left'] = df['days_left']
        
        st.write('The dataframe after preprocessing is:')
        st.write(df)
        if st.button('Predict_Batch_Unprocessed'):
            price = []
            for i in df.index:

                json_data = {
                    'Airline': str(df['airline'].values[i]),
                    'Source_city': str(df['source_city'].values[i]),
                    'Destination_city': str(df['destination_city'].values[i]),
                    'Class': str(df['class'].values[i]),
                    'Stops': str(df['stops'].values[i]),
                    'Departure_time': str(df['departure_time'].values[i]),
                    'Arrival_time': str(df['arrival_time'].values[i]),
                    'Duration': str(df['duration'].values[i]),
                    'Days_left': str(df['days_left'].values[i])
                }
                response = requests.post('http://127.0.0.1:8000/predict', json=json_data)
                prediction = response.json()
                
                #st.write('The predicted price of the flight is', prediction['prediction'])
                price.append(prediction['prediction'])
            df['Price'] = price

            st.write('The dataframe after prediction is:')
            st.write(df)



#If batch prediction is selected as processed csv then processed_csv() function is called
if batch_prediction == 'Processed CSV':
    processed_csv()

#If batch prediction is selected as unprocessed csv then unprocessed_csv() function is called
elif batch_prediction == 'Unprocessed CSV':
    unprocessed_csv()

# Asking the user to enter the number of past predictions to be displayed
n = st.number_input('Enter the number of past predictions to be displayed', min_value=1, max_value=100000)

if st.button('Get Past Predictions'): 
    
    # Sending a GET request to the API
    if n!=None:
        response = requests.get(f'http://127.0.0.1:8000/past', params={'n': n})
        # Getting the predictions
        predictions = response.json()
        # Displaying the predictions as a table
        st.write(pd.DataFrame(predictions))



    