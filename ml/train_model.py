import os
import joblib
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from app import create_app
from app.models.property import Property


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "rent_model.pkl")


def fetch_data():
    app = create_app()

    with app.app_context():
        properties = Property.query.all()

        data = []
        for p in properties:
            days_old = (
                (datetime.utcnow() - p.created_at).days
                if p.created_at else 180
            )

            data.append({
                "city": p.city.lower(),
                "locality": p.locality.lower(),
                "bhk": p.bhk,
                "sqft": p.sqft,
                "furnishing": p.furnishing,
                "days_old": days_old,
                "rent": p.rent
            })

        return pd.DataFrame(data)


def train():
    df = fetch_data()

    if df.empty:
        raise Exception("Database has no data.")

    X = df[[
        "city",
        "locality",
        "bhk",
        "sqft",
        "furnishing",
        "days_old"
    ]]
    y = df["rent"]

    categorical = ["city", "locality", "furnishing"]
    numeric = ["bhk", "sqft", "days_old"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", "passthrough", numeric)
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=250,
            random_state=42
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)

    print("Model trained.")
    print("MAE:", round(mae, 2))

    joblib.dump(model, MODEL_PATH)
    print("Model saved at:", MODEL_PATH)


if __name__ == "__main__":
    train()