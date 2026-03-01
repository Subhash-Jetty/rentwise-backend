import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "rent_model.pkl")

model = None

def get_model():
    global model
    if model is None:
        print("Loading model...")
        model = joblib.load(MODEL_PATH)
        print(f"MODEL LOADED FROM: {MODEL_PATH}")
    return model


def predict_rent(city, locality, bedrooms, area_sqft):
    model_instance = get_model()

    input_data = pd.DataFrame([{
        "city": city,
        "locality": locality,
        "bedrooms": bedrooms,
        "area_sqft": area_sqft
    }])

    prediction = model_instance.predict(input_data)

    return float(prediction[0])