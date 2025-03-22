from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bmi import bmi
from micro_nutrition import BMRCalculator
from getData import CSVRepository

import json
import pickle
import numpy as np
import pandas as pd
import ast


app = FastAPI()

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

# data = pd.read_csv(r"cleaned_recipes_2.csv")
data = CSVRepository()
data = data.get_csv_data()


# Pydantic Models
class Info(BaseModel):
    weight: float
    height: float
    gender: str
    age: int
    activity: str
    plan: str
    rate: str | None = None
    bodyFat: float | None = None

class CustomNutrition(BaseModel):
    calories: float
    protein: float
    fat: float
    carb: float
    num_meals: int | None = None
    ingredients: str | None = None


# Endpoints
@app.post("/diet_recommendation")
async def diet_recommendation(info: Info):
    if info.weight <= 0 or info.height <= 0:
        raise HTTPException(status_code=400, detail="Your weight or height must be bigger than 0")
    
    with open("KMeans_Model.pkl", "rb") as file:
        kmeans = pickle.load(file)

    with open("scaler.pkl", "rb") as file:
        Scaler = pickle.load(file)

    calcBmi = bmi(info.weight, info.height).calculate_bmi()
    calcBmr = BMRCalculator(info.gender, info.weight, info.height, info.age, info.activity, info.plan, info.rate).calculate_bmr()
    user_needs = {
    'Calories': calcBmr['totalDailyCaloricNeeds']['value'],
    'FatContent': calcBmr['fat']["preferred"],
    'ProteinContent': calcBmr['protein']["preferred"],
    'CarbohydrateContent': calcBmr['carbohydrates']["preferred"]
    }
    user_df = pd.DataFrame([user_needs])

# Scale the user's feature vector
    user_df_scaled = Scaler.transform(user_df)

    user_cluster = kmeans.predict(user_df_scaled)
    user_cluster = int(user_cluster[0])
    results = data[data['Cluster'] == user_cluster].sample(50)
    results['RecipeIngredientParts'] = results['RecipeIngredientParts'].apply(ast.literal_eval).tolist()
    results['RecipeInstructions'] = results['RecipeInstructions'].apply(ast.literal_eval).tolist()
    results['Images'] = results['Images'].apply(ast.literal_eval).tolist()
    results['DietCategory'] = results['DietCategory'].apply(ast.literal_eval).tolist()

    return {"Bmi": {"bmi": calcBmi[0], "bmiStatus": calcBmi[1], "unit": "kg/cm"}, "Bmr": calcBmr, "Cluster": user_cluster, "Recommendation": jsonable_encoder(results.to_dict(orient='records'))}

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

@app.post("/custom_meal")
async def custom_meal(custom: CustomNutrition):
    custom_nut = {'Calories': custom.calories, 'Protein': custom.protein, 'Fat': custom.fat, 'Carb': custom.carb}

    
    return {"data": ''}