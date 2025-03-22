import requests
import pandas as pd
import io
import time

class CSVRepository:
    def __init__(self):
        # Cache dictionary to store file content
        self.cache = {}
        # File ID and request parameters
        self.file_id = "1yLavd9wcNPMK-P30MN8bLUe8OwF7w6Sj"
        self.params = {
            "id": self.file_id,
            "export": "download",
            "authuser": "0",
            "confirm": "t",
            "uuid": "82d98ece-05e7-44ef-af75-b48e4fda3187",
            "at": "AEz70l5nqt65CznzLDqpFH8hB-Db:1742602351068"
        }

    def get_csv_data(self):
        url = "https://drive.usercontent.google.com/download"
        
        # Check if the file is in cache
        if self.file_id in self.cache:
            print(f"Returning cached data for file ID: {self.file_id}")
            return self.cache[self.file_id]

        # Send GET request to fetch the CSV file
        response = requests.get(url, params=self.params)

        if response.status_code == 200:
            # Read the CSV content from the response
            csv_content = response.content.decode('utf-8')

            # Use pandas to parse the CSV data
            df = pd.read_csv(io.StringIO(csv_content))

            # Store the data in cache
            self.cache[self.file_id] = df

            return df
        else:
            raise Exception(f"Failed to retrieve the CSV file. Status code: {response.status_code}")