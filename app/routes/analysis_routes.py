from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models.property import Property
from app.utils.ml_loader import predict_rent

# ✅ DEFINE BLUEPRINT FIRST
analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")


@analysis_bp.route("/<int:property_id>", methods=["POST"])
@jwt_required(optional=True)
def analyze_property(property_id):

    property_obj = Property.query.get(property_id)

    if not property_obj:
        return jsonify({"error": "Property not found"}), 404

    try:
        predicted = predict_rent(
            property_obj.city,
            property_obj.locality,
            property_obj.bedrooms,
            property_obj.area_sqft
        )

        if predicted is None:
            raise Exception("Prediction failed")

        # ✅ ROUND TO NEAREST ₹100
        predicted = round(float(predicted) / 100) * 100

    except Exception as e:
        print("PREDICTION ERROR:", e)
        return jsonify({
            "market_analysis": {
                "predicted_rent": 0,
                "difference": 0,
                "market_status": "Prediction failed",
                "message": "Unable to estimate market value."
            }
        })

    actual_rent = round(property_obj.rent)
    difference = actual_rent - predicted
    abs_diff = abs(difference)

    if difference > 2000:
        status = "Overpriced"
        message = f"₹{abs_diff} higher than market average"
    elif difference < -2000:
        status = "Underpriced"
        message = f"₹{abs_diff} lower than market average"
    else:
        status = "Fairly Priced"
        message = f"₹{abs_diff} close to market average"

    lower_bound = round(predicted * 0.9)
    upper_bound = round(predicted * 1.1)

    return jsonify({
        "market_analysis": {
            "predicted_rent": predicted,
            "difference": difference,
            "market_status": status,
            "message": message,
            "market_range": {
                "low": lower_bound,
                "high": upper_bound
            }
        }
    })