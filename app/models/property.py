from datetime import datetime
from app import db
from flask import current_app
from app.models.property_image import PropertyImage

class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)

    city = db.Column(db.String(100), nullable=False)
    locality = db.Column(db.String(150), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    area_sqft = db.Column(db.Float, nullable=False)

    
    rent = db.Column(db.Integer, nullable=False)

    description = db.Column(db.Text)

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Relationship to owner
    owner = db.relationship("User", backref="properties")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship(
        "Review",
        backref="property",
        lazy=True,
        cascade="all, delete-orphan"
    )

    images = db.relationship(
        "PropertyImage",
        backref="property",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # -----------------------
    # Average Rating
    # -----------------------
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(
            sum(r.rating for r in self.reviews) / len(self.reviews),
            2
        )

    # -----------------------
    # Serialize
    # -----------------------
        # -----------------------
    # Serialize
    # -----------------------
    def to_dict(self):
        from flask import request

        base_url = request.host_url.rstrip("/")

        return {
            "id": self.id,
            "city": self.city,
            "locality": self.locality,
            "bedrooms": self.bedrooms,
            "area_sqft": self.area_sqft,
            "rent": self.rent,
            "description": self.description,
            "average_rating": self.average_rating(),
            "owner_email": self.owner.email if self.owner else None,
            "images": [
                f"{base_url}/uploads/{img.image_filename}"
                for img in self.images
            ],
            "reviews": [
                {
                    "rating": r.rating,
                    "comment": r.comment,
                    "user_id": r.user_id
                }
                for r in self.reviews
            ]
        }