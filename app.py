import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np
import joblib
import pandas as pd
from pydantic import BaseModel
import psycopg2
from io import BytesIO
import json


app = FastAPI()

# Making connection with the database
conn = psycopg2.connect('dbname=flight user=postgres password=postgres host=localhost port=5432')
cur = conn.cursor()

# Function to store the data in the database
def store_data(features):

    
    # Replacing the encoded values with the original values before storing in the database
    features[0] = features[0].replace('0', 'Air_India').replace('1', 'AirAsia').replace('2', 'GO_FIRST').replace('3', 'Indigo').replace('4', 'SpiceJet').replace('5', 'Vistara')
    features[1] = features[1].replace('0', 'Bangalore').replace('1', 'Chennai').replace('2', 'Delhi').replace('3', 'Hyderabad').replace('4', 'Kolkata').replace('5', 'Mumbai')
    features[2] = features[2].replace('0', 'Bangalore').replace('1', 'Chennai').replace('2', 'Delhi').replace('3', 'Hyderabad').replace('4', 'Kolkata').replace('5', 'Mumbai')
    features[3] = features[3].replace('0', 'Business').replace('1', 'Economy')
    features[4] = features[4].replace('0', 'zero').replace('1', 'one').replace('2', 'two_or_more')
    features[5] = features[5].replace('0', 'Early_Morning').replace('1', 'Morning').replace('2', 'Afternoon').replace('3', 'Evening').replace('4', 'Night').replace('5', 'Late_Night')
    features[6] = features[6].replace('0', 'Early_Morning').replace('1', 'Morning').replace('2', 'Afternoon').replace('3', 'Evening').replace('4', 'Night').replace('5', 'Late_Night')
    
    # Query to insert the data into the database
    #cur.execute('INSERT INTO dataset (Airline, Source_city, Destination_city, Class, Stops, Departure_time, Arrival_time, Duration, Days_left, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', features)
    cur.execute('INSERT INTO dataset (airline, source_city, destination_city, class, stops, departure_time, arrival_time, duration, days_left, price,timestamp) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)', (features[0], features[1], features[2], features[3], features[4], features[5], features[6], features[7], features[8], features[9], features[10]))
    conn.commit()

# Function to get the data from the database
def get_data(n):
    # Query to get the data using timestamp

    cur.execute('SELECT * FROM dataset LIMIT %s', (n,))
    data = cur.fetchall()
    return data


model = joblib.load('flight_model.pkl')

class Flight(BaseModel):
    Airline: str
    Source_city: str
    Destination_city: str
    Class: str
    Stops : str
    Departure_time: str
    Arrival_time: str
    Duration: str
    Days_left: str

    

@app.get("/")
def read_root():
    return {"Hi ": "Welcome to the Flight Price Prediction API"}

@app.post("/predict")
async def predict(data : Flight):
    data = data.dict()
    data['Airline'] = data['Airline'].replace('Air_India', '0').replace('AirAsia', '1').replace('GO_FIRST', '2').replace('Indigo', '3').replace('SpiceJet', '4').replace('Vistara', '5')
    data['Source_city'] = data['Source_city'].replace('Bangalore', '0').replace('Chennai', '1').replace('Delhi', '2').replace('Hyderabad', '3').replace('Kolkata', '4').replace('Mumbai', '5')
    data['Destination_city'] = data['Destination_city'].replace('Bangalore', '0').replace('Chennai', '1').replace('Delhi', '2').replace('Hyderabad', '3').replace('Kolkata', '4').replace('Mumbai', '5')
    data['Class'] = data['Class'].replace('Business', '0').replace('Economy', '1')
    data['Stops'] = data['Stops'].replace('zero', '0').replace('one', '1').replace('two_or_more', '2')
    data['Departure_time'] = data['Departure_time'].replace('Early_Morning', '0').replace('Morning', '1').replace('Afternoon', '2').replace('Evening', '3').replace('Night', '4').replace('Late_Night', '5')
    data['Arrival_time'] = data['Arrival_time'].replace('Early_Morning', '0').replace('Morning', '1').replace('Afternoon', '2').replace('Evening', '3').replace('Night', '4').replace('Late_Night', '5')

    Airline = data['Airline']
    Source_city = data['Source_city']
    Destination_city = data['Destination_city']
    Class = data['Class']
    Stops = data['Stops']
    Departure_time = data['Departure_time']
    Arrival_time = data['Arrival_time']
    Duration = data['Duration']
    Days_left = data['Days_left']

    features = [Airline, Source_city, Destination_city, Class, Stops, Departure_time, Arrival_time, Duration, Days_left]
    prediction = model.predict([[Airline, Source_city, Destination_city, Class, Stops, Departure_time, Arrival_time, Duration, Days_left]])
    # appending the predicted price to features
    features.append(prediction[0])
    features.append(pd.Timestamp.now())

    # Sending the features list to a postgreSQL database
    store_data(features)
    

    if prediction[0] < 0:
        prediction[0] = 0
    return {
        'prediction': prediction[0]
    }

@app.get("/pastpredictions")
def past_predictions(n: int, date1: str, time1: str, date2: str, time2: str):
    # Converting the date and time to timestamp
    limit = n
    date1 = date1 + ' ' + time1
    date2 = date2 + ' ' + time2
    date1 = pd.Timestamp(date1)
    date2 = pd.Timestamp(date2)
    # Query to get the data using timestamp including date2
    cur.execute('SELECT * FROM dataset WHERE timestamp >= %s AND timestamp <= %s LIMIT %s',(date1, date2, limit))
    
    data = cur.fetchall()
    # Converting the data to a dataframe
    df = pd.DataFrame(data, columns=['Airline', 'Source_city', 'Destination_city', 'Class', 'Stops', 'Departure_time', 'Arrival_time', 'Duration', 'Days_left', 'Price', 'timestamp'])
    # Converting the timestamp to date and time
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    # Converting the dataframe to a dictionary
    data = df.to_dict('records')

    return data

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
