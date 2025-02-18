class bmi:
    def __init__(self, w, h):
        
        self.weight = w * 2.20462262 # weight in pounds
        self.hegit = h * 0.3937007874 # height in inches
        self.bmi = ((self.weight * 703) / self.hegit ** 2) 
    
    def calculate_bmi(self):
        classes = {
            "Underweight" : 18.5,
            "Normal": 24.9,
            "Overweight":30,
        }
        for key, value in classes.items():
            if self.bmi < value:
                return [round(self.bmi, 1), key]
        return [round(self.bmi, 1), 'Obesity']
    

