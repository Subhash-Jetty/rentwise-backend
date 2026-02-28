import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models.property import Property

# -----------------------------
# CONFIGURATION
# -----------------------------

CITIES = {
    "Hyderabad": {
        "localities": {
            "Gachibowli": 45,
            "Hitech City": 50,
            "Kondapur": 38,
            "Madhapur": 48,
            "Manikonda": 30,
            "Kukatpally": 28,
        }
    },
    "Bangalore": {
        "localities": {
            "Whitefield": 55,
            "Electronic City": 32,
            "Indiranagar": 70,
            "Koramangala": 65,
            "HSR Layout": 52,
            "Marathahalli": 40,
        }
    },
    "Mumbai": {
        "localities": {
            "Andheri": 85,
            "Bandra": 120,
            "Powai": 95,
            "Goregaon": 75,
            "Thane": 60,
            "Navi Mumbai": 55,
        }
    },
    "Delhi": {
        "localities": {
            "Saket": 60,
            "Dwarka": 40,
            "Rohini": 35,
            "Lajpat Nagar": 55,
            "Karol Bagh": 45,
        }
    },
    "Chennai": {
        "localities": {
            "OMR": 35,
            "Adyar": 55,
            "Velachery": 38,
            "Anna Nagar": 50,
            "T Nagar": 48,
        }
    },
    "Pune": {
        "localities": {
            "Hinjewadi": 30,
            "Kharadi": 40,
            "Viman Nagar": 42,
            "Baner": 45,
            "Wakad": 28,
        }
    }
}

FURNISHING_MULTIPLIER = {
    "unfurnished": 1.0,
    "semi": 1.15,
    "full": 1.30
}

BHK_SQFT_RANGE = {
    1: (400, 700),
    2: (700, 1200),
    3: (1100, 1800),
    4: (1600, 2500)
}

RECORDS_PER_CITY = 2000


# -----------------------------
# SEED LOGIC
# -----------------------------

def generate_property(city, locality, base_price_per_sqft):
    bhk = random.choice([1, 2, 3, 4])
    sqft_min, sqft_max = BHK_SQFT_RANGE[bhk]
    sqft = random.randint(sqft_min, sqft_max)

    furnishing = random.choice(["unfurnished", "semi", "full"])
    multiplier = FURNISHING_MULTIPLIER[furnishing]

    # base rent calculation
    rent = sqft * base_price_per_sqft * multiplier

    # controlled noise ±10%
    noise = random.uniform(0.9, 1.1)
    rent *= noise

    rent = round(rent, -2)  # round to nearest 100

    deposit = rent * random.randint(3, 6)

    created_at = datetime.utcnow() - timedelta(days=random.randint(0, 365))

    return Property(
        city=city,
        locality=locality,
        bhk=bhk,
        sqft=sqft,
        rent=rent,
        deposit=deposit,
        furnishing=furnishing,
        created_at=created_at
    )


def seed():
    app = create_app()

    with app.app_context():
        print("Clearing existing data...")
        db.session.query(Property).delete()
        db.session.commit()

        total_records = 0

        print("Generating data...")

        for city, city_data in CITIES.items():
            localities = city_data["localities"]

            for _ in range(RECORDS_PER_CITY):
                locality = random.choice(list(localities.keys()))
                base_price = localities[locality]

                property_obj = generate_property(city, locality, base_price)
                db.session.add(property_obj)
                total_records += 1

        db.session.commit()

        print(f"Seeding complete. Total records inserted: {total_records}")


if __name__ == "__main__":
    seed()