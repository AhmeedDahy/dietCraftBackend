from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bmi import bmi
from micro_nutrition import BMRCalculator
import json

app = FastAPI()

origins = [
    "https://diet-craft-vite.vercel.app",  # Allow your production frontend domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Info(BaseModel):
  weight: float
  height: float
  gender: str
  age: int
  activity_level: str
  goal: str
  rate: str | None = None


@app.post("/diet_recommendation")
async def diet_recommendation(info: Info):
  if info.weight <= 0 or info.height <= 0:
    return {"error": "Your weight or height must be bigger than 0"}
  
  calcBmi = bmi(info.weight, info.height).calculate_bmi()
  calcBmr = BMRCalculator(info.gender, info.weight, info.height, info.age, info.activity_level, info.goal, info.rate).calculate_bmr()
  return {"Bmi":{"bmi" : calcBmi[0] ,'bmiStatus' : calcBmi[1] , "unit" : "kg/cm"}, "Bmr" : calcBmr }
  

# Path to your JSON file
JSON_FILE_PATH = "food_data.json"
# server for ur dataset
@app.get("/food-data")
async def get_json_data():
    try:
        with open(JSON_FILE_PATH, "r") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {"error": "File not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}
