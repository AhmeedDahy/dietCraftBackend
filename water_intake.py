def calcWaterIntake(weight_kg, activityLevel):
    activity_levels = {
    "sedentary": 0,
    "lightlyActive":  30 , 
    "moderateActivity": 45,
    "active": 60,
    "veryActive": 90
}
    weight_lbs = weight_kg * 2.205
    
    water_intake_oz = 0.5 * weight_lbs
    
    water_intake_liters = water_intake_oz / 33.814
    exercise_minutes = activity_levels[activityLevel]
    if exercise_minutes > 0:
        extra_water_liters = (exercise_minutes / 30.0) * (12 / 33.814)
        water_intake_liters += extra_water_liters

    cups = (water_intake_liters * 1000) / 200

    return {'liter':round(water_intake_liters, 2),"cups": round(cups)}
