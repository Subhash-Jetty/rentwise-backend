import os
import joblib
import pandas as pd

# Get absolute path to model file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "rent_model.pkl")

# Load model once when app starts
try:
    model = joblib.load(MODEL_PATH)
    print(f"MODEL LOADED FROM: {MODEL_PATH}")
except Exception as e:
    print("Error loading model:", e)
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