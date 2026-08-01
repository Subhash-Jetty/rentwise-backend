import os

from app import db
from app.models.property import Property
from app.models.user import User


DEMO_PROPERTIES = [
    {
        "city": "Hyderabad",
        "locality": "Madhapur",
        "bedrooms": 2,
        "area_sqft": 1050,
        "rent": 42000,
        "description": "Bright 2 BHK near offices and metro access.",
    },
    {
        "city": "Hyderabad",
        "locality": "Gachibowli",
        "bedrooms": 3,
        "area_sqft": 1550,
        "rent": 65000,
        "description": "Spacious family apartment close to schools and tech parks.",
    },
    {
        "city": "Bengaluru",
        "locality": "Indiranagar",
        "bedrooms": 2,
        "area_sqft": 980,
        "rent": 58000,
        "description": "Walkable apartment with cafes, transit, and city access.",
    },
    {
        "city": "Mumbai",
        "locality": "Powai",
        "bedrooms": 1,
        "area_sqft": 650,
        "rent": 52000,
        "description": "Compact lake-side rental with excellent connectivity.",
    },
    {
        "city": "Chennai",
        "locality": "Adyar",
        "bedrooms": 3,
        "area_sqft": 1450,
        "rent": 56000,
        "description": "Quiet residential home near parks and daily essentials.",
    },
    {
        "city": "Pune",
        "locality": "Baner",
        "bedrooms": 2,
        "area_sqft": 1100,
        "rent": 39000,
        "description": "Modern rental with strong commute links and amenities.",
    },
]


def seed_demo_data():
    if os.environ.get("SEED_DEMO_DATA", "true").lower() != "true":
        return

    if Property.query.first():
        return

    email = os.environ.get("DEMO_OWNER_EMAIL", "demo.owner@rentwise.app")
    password = os.environ.get("DEMO_OWNER_PASSWORD", "DemoRentwise123!")

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, role="renter")
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

    for data in DEMO_PROPERTIES:
        db.session.add(Property(owner_id=user.id, **data))

    db.session.commit()
