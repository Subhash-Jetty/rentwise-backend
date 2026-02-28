from datetime import datetime
from app import db


class PropertyImage(db.Model):
    __tablename__ = "property_images"

    id = db.Column(db.Integer, primary_key=True)

    image_filename = db.Column(db.String(300), nullable=False)

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)