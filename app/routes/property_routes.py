from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from sqlalchemy import desc, asc
import os
from app.utils.r2_client import get_r2_client
import uuid
from app.extensions import db
import os
from app.utils.r2_upload import upload_to_r2
from app import db
from app.models.property import Property
from app.models.user import User
from app.models.review import Review
from app.models.wishlist import Wishlist

property_bp = Blueprint("properties", __name__, url_prefix="/properties")


# =========================================================
# CREATE PROPERTY (MULTIPLE IMAGES)
# =========================================================
@property_bp.route("/", methods=["POST"])
@jwt_required()
def create_property():
    from flask_jwt_extended import get_jwt_identity
    from app.models.user import User

    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)

    if not user or user.role != "renter":
        return jsonify({"error": "Only renters can create properties"}), 403

    try:
        city = request.form.get("city")
        locality = request.form.get("locality")

        city = city.strip().title()
        locality = locality.strip().title()

        bedrooms = int(request.form.get("bedrooms"))
        area_sqft = float(request.form.get("area_sqft"))
        rent = round(float(request.form.get("rent")))
        description = request.form.get("description", "")

        if not city or not locality:
            return jsonify({"error": "City and locality required"}), 400

        new_property = Property(
            city=city,
            locality=locality,
            bedrooms=bedrooms,
            area_sqft=area_sqft,
            rent=rent,
            description=description,
            owner_id=user_id
        )

        db.session.add(new_property)
        db.session.flush()

        images = request.files.getlist("images")
        from app.models.property_image import PropertyImage

        for image in images:
            if image and image.filename != "":
                image_url = upload_to_r2(image)

                property_image = PropertyImage(
                    image_filename=image_url,
                    property_id=new_property.id
                )

                db.session.add(property_image)

        db.session.commit()
        return jsonify({"message": "Property created"}), 201

    except Exception as e:
        db.session.rollback()
        print("CREATE ERROR:", e)
        return jsonify({"error": "Creation failed"}), 500

# =========================================================
# GET ALL (PAGINATION + SEARCH + SORT)
# =========================================================
@property_bp.route("/all", methods=["GET"])
@jwt_required(optional=True)
def get_all_properties():

    current_user_id = None
    try:
        current_user_id = int(get_jwt_identity())
    except:
        current_user_id = None

    city = request.form.get("city")
    if city:
      city = city.strip().lower().capitalize()
    locality = request.args.get("locality")
    bedrooms = request.args.get("bedrooms")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    sort = request.args.get("sort")

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 9))

    query = Property.query

    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))

    if locality:
        query = query.filter(Property.locality.ilike(f"%{locality}%"))

    if bedrooms:
        if bedrooms == "4":
            query = query.filter(Property.bedrooms >= 4)
        else:
            query = query.filter(Property.bedrooms == int(bedrooms))

    if min_price:
        query = query.filter(Property.rent >= float(min_price))

    if max_price:
        query = query.filter(Property.rent <= float(max_price))

    if sort == "low":
        query = query.order_by(asc(Property.rent))
    elif sort == "high":
        query = query.order_by(desc(Property.rent))
    else:
        query = query.order_by(desc(Property.created_at))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    properties_list = []

    for p in pagination.items:
        property_data = p.to_dict()

        # 🔥 Inject wishlist flag
        if current_user_id:
            exists = Wishlist.query.filter_by(
                user_id=current_user_id,
                property_id=p.id
            ).first()
            property_data["is_in_wishlist"] = bool(exists)
        else:
            property_data["is_in_wishlist"] = False

        properties_list.append(property_data)

    return jsonify({
        "properties": properties_list,
        "current_page": pagination.page,
        "total_pages": pagination.pages,
        "total_items": pagination.total
    }), 200
@property_bp.route("/filters", methods=["GET"])
def get_filters():

    properties = Property.query.all()
    city_map = {}

    for p in properties:
        if p.city not in city_map:
            city_map[p.city] = set()
        city_map[p.city].add(p.locality)

    # Convert sets to lists
    for city in city_map:
        city_map[city] = list(city_map[city])

    return jsonify({
        "cities": city_map
    }), 200

# =========================================================
# GET SINGLE PROPERTY
# =========================================================
@property_bp.route("/<int:property_id>", methods=["GET"])
def get_property(property_id):

    property_obj = db.session.get(Property, property_id)

    if not property_obj:
        return jsonify({"error": "Property not found"}), 404

    return jsonify(property_obj.to_dict()), 200


# =========================================================
# GET MY PROPERTIES (RENTER)
# =========================================================
@property_bp.route("/mine", methods=["GET"])
@jwt_required()
def get_my_properties():

    user_id = int(get_jwt_identity())

    properties = Property.query.filter_by(
        owner_id=user_id
    ).order_by(desc(Property.created_at)).all()

    return jsonify([p.to_dict() for p in properties]), 200


# =========================================================
# UPDATE PROPERTY
# =========================================================
@property_bp.route("/<int:property_id>", methods=["PUT"])
@jwt_required()
def update_property(property_id):

    user_id = int(get_jwt_identity())
    property_obj = db.session.get(Property, property_id)

    if not property_obj:
        return jsonify({"error": "Property not found"}), 404

    if property_obj.owner_id != user_id:
        return jsonify({"error": "Not authorized"}), 403

    data = request.get_json()

    try:
        if data.get("city"):
            property_obj.city = data.get("city").strip().title()
        if data.get("locality"):
            property_obj.locality = data.get("locality").strip().title()
        property_obj.bedrooms = int(data.get("bedrooms", property_obj.bedrooms))
        property_obj.area_sqft = float(data.get("area_sqft", property_obj.area_sqft))
        property_obj.rent = round(float(data.get("rent", property_obj.rent)))
        property_obj.description = data.get("description", property_obj.description)

        db.session.commit()

        return jsonify({"message": "Updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print("UPDATE ERROR:", e)
        return jsonify({"error": "Update failed"}), 500


# =========================================================
# DELETE PROPERTY
# =========================================================
@property_bp.route("/<int:property_id>", methods=["DELETE"])
@jwt_required()
def delete_property(property_id):

    user_id = int(get_jwt_identity())
    property_obj = db.session.get(Property, property_id)

    if not property_obj:
        return jsonify({"error": "Property not found"}), 404

    if property_obj.owner_id != user_id:
        return jsonify({"error": "Not authorized"}), 403

    db.session.delete(property_obj)
    db.session.commit()

    return jsonify({"message": "Deleted successfully"}), 200


# =========================================================
# ADD REVIEW (ONE PER USER + NO SELF REVIEW)
# =========================================================
@property_bp.route("/<int:property_id>/review", methods=["POST"])
@jwt_required()
def add_review(property_id):

    user_id = int(get_jwt_identity())
    data = request.get_json()

    rating = int(data.get("rating"))
    comment = data.get("comment", "")

    if rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be between 1-5"}), 400

    property_obj = db.session.get(Property, property_id)

    if not property_obj:
        return jsonify({"error": "Property not found"}), 404

    # 🚫 Prevent renter reviewing own property
    if property_obj.owner_id == user_id:
        return jsonify({
            "error": "You cannot review your own property."
        }), 400

    # 🚫 Prevent multiple reviews
    existing_review = Review.query.filter_by(
        user_id=user_id,
        property_id=property_id
    ).first()

    if existing_review:
        return jsonify({
            "error": "You have already reviewed this property."
        }), 400

    review = Review(
        rating=rating,
        comment=comment,
        user_id=user_id,
        property_id=property_id
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "Review added"}), 201


# =========================================================
# ADD TO WISHLIST
# =========================================================
@property_bp.route("/<int:property_id>/wishlist", methods=["POST"])
@jwt_required()
def add_to_wishlist(property_id):

    user_id = int(get_jwt_identity())

    existing = Wishlist.query.filter_by(
        user_id=user_id,
        property_id=property_id
    ).first()

    if existing:
        return jsonify({"message": "Already added"}), 200

    wishlist = Wishlist(
        user_id=user_id,
        property_id=property_id
    )

    db.session.add(wishlist)
    db.session.commit()

    return jsonify({"message": "Added to wishlist"}), 201
@property_bp.route("/<int:property_id>/wishlist", methods=["DELETE"])
@jwt_required()
def remove_from_wishlist(property_id):

    user_id = int(get_jwt_identity())

    wishlist_item = Wishlist.query.filter_by(
        user_id=user_id,
        property_id=property_id
    ).first()

    if not wishlist_item:
        return jsonify({"error": "Not in wishlist"}), 404

    db.session.delete(wishlist_item)
    db.session.commit()

    return jsonify({"message": "Removed from wishlist"}), 200

# =========================================================
# GET WISHLIST
# =========================================================
@property_bp.route("/wishlist", methods=["GET"])
@jwt_required()
def get_wishlist():

    user_id = int(get_jwt_identity())

    wishlist_items = Wishlist.query.filter_by(
        user_id=user_id
    ).all()

    properties = []

    for item in wishlist_items:
        property_obj = db.session.get(Property, item.property_id)
        if property_obj:
            properties.append(property_obj.to_dict())

    return jsonify(properties), 200