from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, conint, confloat, validator, Field

import json
import pickle
import numpy as np
import pandas as pd

from bmi import bmi
from micro_nutrition import BMRCalculator


app = FastAPI()

# Constants for validation
MIN_HEIGHT = 100
MAX_HEIGHT = 250
MIN_WEIGHT = 40
MAX_WEIGHT = 300
MIN_AGE = 13
MAX_AGE = 110

# CORS Configuration
origins = [
    "https://diet-craft-vite.vercel.app",  # Allow your production frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


data = pd.read_csv(r"C:\Users\Dahy\cleaned_recipes_2.csv")
# data = CSVRepository()
# data = data.get_csv_data()




# Pydantic Models
class Info(BaseModel):
    height: float = Field(..., ge=MIN_HEIGHT, le=MAX_HEIGHT)
    weight: float = Field(..., ge=MIN_WEIGHT, le=MAX_WEIGHT)
    age: int = Field(..., ge=MIN_AGE, le=MAX_AGE)
    gender: str
    activity: str
    plan: str
    rate: str

    @validator('gender')
    def validate_gender(cls, v):
        if v.lower() not in ['male', 'female']:
            raise ValueError('Gender must be either "male" or "female"')
        return v.lower()

    @validator('activity')
    def validate_activity(cls, v):
        valid_activities = ['sedentary', 'lightlyActive', 'moderateActivity', 'active', 'veryActive']
        if v not in valid_activities:
            raise ValueError(f'Activity must be one of: {", ".join(valid_activities)}')
        return v





# Endpoints
@app.post("/diet_recommendation")
async def diet_recommendation(info: Info):
    try:
        # Load models safely
        try:
            with open("KMeans_Model.pkl", "rb") as file:
                kmeans = pickle.load(file)
            with open("scaler.pkl", "rb") as file:
                scaler = pickle.load(file)
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=f"Model file not found: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading model: {str(e)}")

        # Calculate metrics
        calcBmi = bmi(info.weight, info.height).calculate_bmi()
        calcBmr = BMRCalculator(
            info.gender, 
            info.weight, 
            info.height, 
            info.age, 
            info.activity, 
            info.plan, 
            info.rate
        ).calculate_bmr()

        # Prepare user data for clustering
        user_needs = {
            'Calories': calcBmr['totalDailyCaloricNeeds']['value'],
            'FatContent': calcBmr['fat']["preferred"],
            'ProteinContent': calcBmr['protein']["preferred"],
            'CarbohydrateContent': calcBmr['carbohydrates']["preferred"]
        }
        
        user_df = pd.DataFrame([user_needs])
        user_df_scaled = scaler.transform(user_df)
        
        # Predict cluster
        user_cluster = int(kmeans.predict(user_df_scaled)[0])

        return {
            "Bmi": {
                "bmi": calcBmi[0],
                "bmiStatus": calcBmi[1],
                "unit": "kg/m²"
            },
            "Bmr": calcBmr,
            "Cluster": user_cluster,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    

@app.get("/food-data")
async def get_json_data():
    JSON_FILE_PATH = "food_data.json"
    try:
        with open(JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")


@app.get("/recommended_meals/")
async def search_items(cluster: int):
    if cluster < 0 or cluster > 5:
        raise HTTPException(status_code=400, detail="Cluster must be between 0 and 5")
    
    results = data[data['Cluster'] == cluster].sample(1000,random_state=42+cluster)
    return {"Recommendation": results.to_dict(orient='records')}