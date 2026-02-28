import os
import joblib
import pandas as pd
import numpy as np
from sqlalchemy import and_

from app.models.property import Property


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "rent_model.pkl")


class RentEngine:

    model = None

    # --------------------------------------------------
    # LOAD ML MODEL
    # --------------------------------------------------
    @classmethod
    def load_model(cls):
       if cls.model is None:
          if os.path.exists(MODEL_PATH):
            cls.model = joblib.load(MODEL_PATH)
            print("ML Model Loaded")
          else:
             print("ML model not found at:", MODEL_PATH)

    # --------------------------------------------------
    # BENCHMARK CALCULATION
    # --------------------------------------------------
    @staticmethod
    def calculate_benchmark(comparables, asked_rent):

        rents = sorted([p.rent for p in comparables])

        fair_rent = float(np.mean(rents))
        min_rent = float(min(rents))
        max_rent = float(max(rents))

        overpricing_percent = (
            (asked_rent - fair_rent) / fair_rent
        ) * 100

        percentile = (
            sum(r <= asked_rent for r in rents)
            / len(rents)
        ) * 100

        # Confidence logic
        if len(rents) > 80:
            confidence = "High"
        elif len(rents) > 30:
            confidence = "Medium"
        else:
            confidence = "Low"

        # Market position
        if percentile < 25:
            position = "Below Market"
        elif percentile < 75:
            position = "Market Range"
        else:
            position = "Premium"

        return {
            "comparables_count": len(rents),
            "fair_rent": round(fair_rent, 2),
            "overpricing_percent": round(overpricing_percent, 2),
            "price_range": {
                "min": min_rent,
                "max": max_rent
            },
            "confidence_score": confidence,
            "market_position_label": position,
            "market_position_percentile": round(percentile, 2)
        }

    # --------------------------------------------------
    # ML PREDICTION
    # --------------------------------------------------
    @classmethod
    def ml_predict(cls, city, locality, bhk, sqft):

        cls.load_model()

        if cls.model is None:
            return None

        input_df = pd.DataFrame([{
            "city": city.lower(),
            "locality": locality.lower(),
            "bhk": bhk,
            "sqft": sqft,
            "furnishing": "semi",
            "days_old": 30
        }])

        try:
            prediction = cls.model.predict(input_df)[0]
            return round(float(prediction), 2)
        except Exception as e:
            print("ML prediction error:", e)
            return None

    # --------------------------------------------------
    # MAIN ANALYZE FUNCTION
    # --------------------------------------------------
    @classmethod
    def analyze(cls, city, locality, bhk, sqft, asked_rent):

        comparables = Property.query.filter(
            and_(
                Property.city.ilike(f"%{city}%"),
                Property.locality.ilike(f"%{locality}%"),
                Property.bhk == bhk,
                Property.sqft.between(
                    sqft * 0.85,
                    sqft * 1.15
                )
            )
        ).all()

        if not comparables:
            return {
                "benchmark": None,
                "ml_prediction": {
                    "predicted_rent": cls.ml_predict(city, locality, bhk, sqft)
                }
            }

        benchmark_data = cls.calculate_benchmark(
            comparables,
            asked_rent
        )

        ml_prediction_value = cls.ml_predict(
            city,
            locality,
            bhk,
            sqft
        )

        return {
            "benchmark": benchmark_data,
            "ml_prediction": {
                "predicted_rent": ml_prediction_value
            }
        }