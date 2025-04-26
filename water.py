def water_intake(weight, activity_level):
  # Convert weight to pounds and multiply by 0.5
  water_per_weight = 0.5 * (weight * 2.205)
  adj_water_per_weight = 33.814 / water_per_weight

  water_intake = adj_water_per_weight + ((activity_level / 30) * (12 / 33.814))
  cups = (water_intake * 1000) / 200
  return [water_intake, cups]

print(water_intake(90, 110))  