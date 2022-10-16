import fastapi
import uvicorn
from fastapi import File
from fastapi import FastAPI
from fastapi import UploadFile
import numpy as np
import joblib
import pandas as pd
from pydantic import BaseModel
import json
import psycopg2
from io import BytesIO
import json


app = FastAPI()

# Making connection with the database
conn = psycopg2.connect('dbname=flight user=postgres password=postgres host=localhost port=5432')
cur = conn.cursor()

# Function to store the data in the database
def store_data(features):

    # Saving the data in the database for a preprocessed dataset
    cur.execute('INSERT INTO processed (Airline, Source_city, Destination_city, Class, Stops, Departure_time, Arrival_time,duration,days_left,Price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s)', (features[0], features[1], features[2], features[3], features[4], features[5], features[6], features[7], features[8], features[9]))
    
    # Replacing the encoded values with the original values before storing in the database
    features[0] = features[0].replace('0', 'Air_India').replace('1', 'AirAsia').replace('2', 'GO_FIRST').replace('3', 'Indigo').replace('4', 'SpiceJet').replace('5', 'Vistara')
    features[1] = features[1].replace('0', 'Bangalore').replace('1', 'Chennai').replace('2', 'Delhi').replace('3', 'Hyderabad').replace('4', 'Kolkata').replace('5', 'Mumbai')
    features[2] = features[2].replace('0', 'Bangalore').replace('1', 'Chennai').replace('2', 'Delhi').replace('3', 'Hyderabad').replace('4', 'Kolkata').replace('5', 'Mumbai')
    features[3] = features[3].replace('0', 'Business').replace('1', 'Economy')
    features[4] = features[4].replace('0', 'zero').replace('1', 'one').replace('2', 'two_or_more')
    features[5] = features[5].replace('0', 'Early_Morning').replace('1', 'Morning').replace('2', 'Afternoon').replace('3', 'Evening').replace('4', 'Night').replace('5', 'Late_Night')
    features[6] = features[6].replace('0', 'Early_Morning').replace('1', 'Morning').replace('2', 'Afternoon').replace('3', 'Evening').replace('4', 'Night').replace('5', 'Late_Night')
    
    cur.execute('INSERT INTO dataset (airline, source_city, destination_city, class, stops, departure_time, arrival_time, duration, days_left, price) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (features[0], features[1], features[2], features[3], features[4], features[5], features[6], features[7], features[8], features[9]))
    conn.commit()

# Function to get the data from the database
def get_data(n):


    cur.execute('SELECT * FROM dataset LIMIT %s', (n,))
    data = cur.fetchall()
    return data


model = joblib.load('flight_training_model.joblib')

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

    # Sending the features list to a postgreSQL database
    store_data(features)
    

    if prediction[0] < 0:
        prediction[0] = 0
    return {
        'prediction': prediction[0]
    }

@app.get("/past")
# async function to n rows of data from the database
async def past(n : int):
    data = get_data(n)
    return data
    


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)