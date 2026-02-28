import joblib
import os
from datetime import datetime

MODEL_PATH = os.path.join(os.getcwd(), "ml", "rent_model.pkl")

pipeline = joblib.load(MODEL_PATH)


class MLEngine:

    @staticmethod
    def predict(city, locality, bhk, sqft, furnishing):

        days_old = 0  # Assume fresh listing for prediction

        input_data = [{
            "city": city,
            "locality": locality,
            "bhk": bhk,
            "sqft": sqft,
            "furnishing": furnishing,
            "days_old": days_old
        }]

        prediction = pipeline.predict(input_data)[0]

        return round(float(prediction), 2)