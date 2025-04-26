#!/usr/bin/env python
# coding: utf-8

# In[5]:


class BMRCalculator:
    def __init__(self, gender, weight, height, age, activity_level, goal, rate=None):
        self.gender = gender
        self.weight = weight
        self.height = height
        self.age = age
        self.activity_level = activity_level
        self.goal = goal
        self.rate = rate

    def calculate_bmr(self):
        # Mifflin-St Jeor Equation
        bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + (5 if self.gender == "male" else -161)

        # Activity level multiplier
        activity_levels = {
            "sedentary": 1.2,
            "lightlyActive": 1.375,
            "moderateActivity": 1.55,
            "active": 1.725,
            "veryActive": 1.9
        }

        total_calories = bmr * activity_levels[self.activity_level]

        # Weight goal adjustment
        if self.goal in ["loss", "gain"]:
            adjustment = 1000 if self.rate == "1" else 500
            total_calories += -adjustment if self.goal == "loss" else adjustment

        # Macronutrient calculation
        protein_min = 1.2 * self.weight
        protein_max = 2.2 * self.weight
        preferred_protein = 1.6 * self.weight

        fat_min = 0.2 * total_calories / 9
        fat_max = 0.3 * total_calories / 9
        preferred_fat = 0.25 * total_calories / 9

        protein_cal_min = protein_min * 4
        protein_cal_max = protein_max * 4
        protein_cal_pref = preferred_protein * 4

        fat_cal_min = fat_min * 9
        fat_cal_max = fat_max * 9
        fat_cal_pref = preferred_fat * 9

        carb_cal_min = total_calories - (protein_cal_max + fat_cal_max)
        carb_cal_pref = total_calories - (protein_cal_pref + fat_cal_pref)
        carb_cal_max = total_calories - (protein_cal_min + fat_cal_min)

        carbs_min = carb_cal_min / 4
        carbs_pref = carb_cal_pref / 4
        carbs_max = carb_cal_max / 4

        results = {
            "BMR":{"value" :round(bmr, 2), "unit" : "kcal" } ,
            "totalDailyCaloricNeeds":{"value":round(total_calories, 2) , "unit" : "kcal" } ,
            "protein": {"min": round(protein_min, 1) , "preferred" : round(preferred_protein, 1) , "max" : round(protein_max, 1), "unit" : "g"},
            "fat": {"min": round(fat_min, 1) , "preferred" : round(preferred_fat, 1) , "max" : round(fat_max, 1), "unit" : "g"},
            "carbohydrates": {"min": round(carbs_min, 1) , "preferred" : round(carbs_pref, 1) , "max" : round(carbs_max, 1), "unit" : "g"}
        }

        return results


