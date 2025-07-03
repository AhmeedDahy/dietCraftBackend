from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, Field

import json
import pickle
import pandas as pd
import random
from bmi import bmi
from micro_nutrition import BMRCalculator
from water_intake import calcWaterIntake


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

class MessageInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)



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
        waterClac = calcWaterIntake(info.weight,info.activity)

        # Prepare user data for clustering
        # per meal
        user_needs = {
            'Calories': calcBmr['BMR']['value'] / 6,
            'FatContent': calcBmr['fat']["preferred"] / 6,
            'ProteinContent': calcBmr['protein']["preferred"] / 6,
            'CarbohydrateContent': calcBmr['carbohydrates']["preferred"] / 6
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
            "WaterIntake": waterClac,
            "Cluster": user_cluster
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    



@app.get("/recommended_meals/")
async def search_items(cluster: int):
    if cluster < 0 or cluster > 4:
        raise HTTPException(status_code=400, detail="Cluster must be between 0 and 4")
    
    file_name = f"food{'' if cluster == 0 else cluster}.json"

    try:
        with open(file_name, "r") as f:
            data = json.load(f)

        # Extract list of recipes
        recipes = list(data.values())

        # Take a sample of up to 1000 items
        sample = random.sample(recipes, min(1000, len(recipes)))

        return sample

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_name} not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Error decoding JSON from {file_name}")





# @app.post("/chat")
# async def chat(request: MessageInput):
#     try:
#         response = ollama.chat(model="qwen3:1.7b",
#                             messages=[{"role": "system", "content": 'You are a helpful assistant. Only return the final answer directly. Do not explain or show your reasoning. Avoid using <think> tags.'},
#                             {"role": "user", "content": request.message}])['message']['content']
#         row_response = re.split(r'</think>\s*', response, maxsplit=1)[-1]
#         return {
#             "response": row_response.strip(),
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))