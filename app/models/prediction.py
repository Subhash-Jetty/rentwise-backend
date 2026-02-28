from datetime import datetime
from app import db

class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)

    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)

    predicted_rent = db.Column(db.Float, nullable=False)

    fairness_score = db.Column(db.Float, nullable=False)

    is_overpriced = db.Column(db.Boolean, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)