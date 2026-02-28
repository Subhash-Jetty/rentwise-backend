import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "ml", "rent_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    print("MODEL LOADED FROM:", MODEL_PATH)
except Exception as e:
    print("MODEL LOAD ERROR:", e)
    model = None


def predict_rent(city, locality, bedrooms, area_sqft):

    if model is None:
        raise Exception("Model not loaded")

    input_data = pd.DataFrame([{
        "city": city,
        "locality": locality,
        "bedrooms": bedrooms,
        "area_sqft": area_sqft
    }])

    prediction = model.predict(input_data)

    return float(prediction[0])