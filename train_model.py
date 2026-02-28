import pandas as pd
import numpy as np
import joblib
import json

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

np.random.seed(42)

city_config = {
    "Hyderabad": {"base_rate": 28, "localities": {"Madhapur": 1.35, "Gachibowli": 1.40, "Kondapur": 1.25}},
    "Chennai": {"base_rate": 26, "localities": {"T Nagar": 1.35, "Adyar": 1.30, "Velachery": 1.20}},
    "Bengaluru": {"base_rate": 32, "localities": {"Whitefield": 1.30, "Koramangala": 1.45, "Indiranagar": 1.50}},
    "Mumbai": {"base_rate": 55, "localities": {"Bandra": 1.50, "Andheri": 1.30, "Powai": 1.25}},
    "Pune": {"base_rate": 30, "localities": {"Hinjewadi": 1.30, "Kothrud": 1.20, "Baner": 1.30}},
    "Vijayawada": {"base_rate": 20, "localities": {"Benz Circle": 1.30, "Governorpet": 1.20}},
    "Guntur": {"base_rate": 16, "localities": {"Brodipet": 1.25, "Arundelpet": 1.20}}
}

data = []

for city, config in city_config.items():
    base_rate = config["base_rate"]
    localities = config["localities"]

    for _ in range(2000):
        locality = np.random.choice(list(localities.keys()))
        locality_multiplier = localities[locality]

        bedrooms = np.random.randint(1, 5)
        area_sqft = np.random.randint(450, 2500)

        bedroom_premium = bedrooms * 2000

        rent = (
            area_sqft * base_rate * locality_multiplier
            + bedroom_premium
            + np.random.randint(-3000, 3000)
        )

        rent = max(5000, rent)

        data.append([city, locality, bedrooms, area_sqft, rent])

df = pd.DataFrame(data, columns=[
    "city",
    "locality",
    "bedrooms",
    "area_sqft",
    "rent"
])

print("Dataset size:", df.shape)

X = df[["city", "locality", "bedrooms", "area_sqft"]]
y = df["rent"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), ["city", "locality"]),
    ("num", "passthrough", ["bedrooms", "area_sqft"])
])

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(
    n_estimators=90,        
    max_depth=12,           
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
))
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)

metrics = {
    "r2_score": round(r2_score(y_test, y_pred), 4),
    "mae": round(mean_absolute_error(y_test, y_pred), 2),
    "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
    "dataset_size": len(df)
}

joblib.dump(pipeline, "rent_model.pkl", compress=3)

with open("model_metrics.json", "w") as f:
    json.dump(metrics, f)

print("Model trained and saved successfully.")
print(metrics)