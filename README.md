# DietCraft API

## Overview

This FastAPI-based backend provides dietary recommendations planning based on user input. The API utilizes machine learning clustering to recommend meals that match the user's nutritional needs.

## Features

- **Diet Recommendation**: Provides personalized diet recommendations based on user BMI, BMR, and nutritional requirements.
- **Machine Learning**: Uses KMeans clustering and scaling techniques to classify users into diet categories based on nutritional needs.
- **CORS Enabled**: Configured for frontend integration with a Vercel-hosted app.

## Requirements

- Python 3.9+
- FastAPI
- Pandas
- NumPy
- Pickle
- Pydantic
- JSON
- See `requirements.txt` for full dependency list

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/AhmeedDahy/dietCraftBackend.git
   cd dietCraftBackend
   ```

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Run the API:
   ```sh
   uvicorn app:app --reload --port=344
   ```

# API Endpoints

This document outlines the available endpoints in the Diet Craft API.

---

## **1. Diet Recommendation**

### `POST /diet_recommendation`

**Description:**  
Generates a personalized diet recommendation based on user BMI, BMR, and nutritional needs.

**Request Body:**

```json
{
  "weight": 70.5,
  "height": 175,
  "gender": "male",
  "age": 30,
  "activity": "moderate",
  "plan": "maintain",
  "rate": "1"
}
```

**Response Body:**

```json
{
  "Bmi": {...},
  "Bmr": {...},
  "Cluster": 1:4,
}
```

## **2. Recommended meals**

### `GET /recommended_meals`

**Description:**  
Get your recommended meals based on your nutritional needs.

**Search query: number(1:4)**

**Response Body:**

```json
{
  "Meals":[{...}, {...}, {...}, {...}, .....]
}
```
