import base64
from ctypes.wintypes import SIZE
from io import StringIO
import streamlit as st
import pickle
import pandas as pd 
import numpy as np
import datetime
import time
import emoji
import warnings
import csv
import PIL.Image as Image
warnings.filterwarnings('ignore')

# Load the model
model = pickle.load(open('flight_model.pkl', 'rb'))

# Putting a image above the title
img = Image.open('Epita.png')
st.image(img, width=500)
# Title
st.title('Flight Price Prediction')




# Streamlit subheader
st.subheader('Enter the details of the flight')


#airline_dict = {'Air_India': 0, 'AirAsia': 1, 'GO_FIRST': 2, 'Indigo': 3, 'SpiceJet': 4, 'Vistara': 5}
#source_city_dict = {'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5}
#destination_city_dict = {'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5}
#class_dict = {'Business': 0, 'Economy': 1}
#departure_time_dict = {'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5}
#arrival_time_dict = {'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5}
#stops_dict = {'zero': 0, 'one': 1, 'two_or_more': 2}

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

# Submit button
if st.button('Predict'):
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
    
    # Predicting the price
    prediction = model.predict(df)
    
    # Displaying the price
    st.success('The price of the flight is {}'.format(prediction[0]))


# Button to predict the price to batch prediction

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

    # Downloading the table as a csv file
        def filedownload(df):
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
            href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download CSV File</a>'
            return href
    
        st.markdown(filedownload(df), unsafe_allow_html=True)

    #Creating a button to preprocess the csv file
    if st.button('Preprocess'):
        df1 = df.copy()
        for i in range(len(df)):
            # Converting the categorical variables to numerical variables according to i in the loop
            df1['Airline'][i] = df1['airline'][i].map({'Air_India': 0, 'AirAsia': 1, 'GO_FIRST': 2, 'Indigo': 3, 'SpiceJet': 4, 'Vistara': 5})
            df1['Source_city'][i] = df1['source_city'][i].map({'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5})
            df1['Destination_city'][i] = df1['destination_city'][i].map({'Bangalore': 0, 'Chennai': 1, 'Delhi': 2, 'Hyderabad': 3, 'Kolkata': 4, 'Mumbai': 5})
            df1['Class'][i] = df1['class'][i].map({'Business': 0, 'Economy': 1})
            df1['Stops'][i] = df1['stops'][i].map({'zero': 0, 'one': 1, 'two_or_more': 2})
            df1['Departure_time'][i] = df1['departure_time'][i].map({'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5})
            df1['Arrival_time'][i] = df1['arrival_time'][i].map({'Early_Morning': 0, 'Morning': 1, 'Afternoon': 2, 'Evening': 3, 'Night': 4, 'Late_Night': 5})
            
            # Converting the values in each row according to the mapping
            
            # Displaying the table
        st.write(df1)

batch_prediction = st.selectbox('Batch Prediction', ('Processed CSV', 'Unprocessed CSV'))

#If batch prediction is selected as processed csv then processed_csv() function is called
if batch_prediction == 'Processed CSV':
    processed_csv()
