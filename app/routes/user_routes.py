from flask import render_template, Blueprint, request
from bson.objectid import ObjectId
from app import mongo
from app.utils import jwt_required
from app.models.item_model import ItemModel
from app.models.request_model import RequestModel
from app.models.user_model import UserModel
from app.services.email_service import send_email

user_bp = Blueprint("user", __name__, url_prefix="/user")

# ============================================================
# USER DASHBOARD (HTML)
# ============================================================
@user_bp.route("/dashboard", methods=["GET"])
def user_dashboard():
    return render_template("user_dashboard.html")


# ============================================================
# USER DASHBOARD DATA API
# ============================================================
@user_bp.route("/dashboard-data", methods=["GET"])
@jwt_required
def user_dashboard_data():
    user_id = request.user["user_id"]

    items = ItemModel.get_items_by_user(user_id)
    requests = RequestModel.get_requests_by_user(user_id)

    return {
        "items_count": len(items),
        "requests_count": len(requests)
    }, 200


# ============================================================
# ADD ITEM PAGE (HTML)
# ============================================================
@user_bp.route("/add-item-page", methods=["GET"])
def add_item_page():
    return render_template("add_item.html")


# ============================================================
# ADD ITEM API + EMAIL
# ============================================================
@user_bp.route("/add-item", methods=["POST"])
@jwt_required
def add_item():
    data = request.json

    item = {
        "user_id": request.user["user_id"],
        "itemName": data.get("itemName"),
        "category": data.get("category"),
        "description": data.get("description"),
        "status": "Pending"
    }

    mongo.db.items.insert_one(item)

    # --------------------------------------
    # SEND EMAIL TO USER
    # --------------------------------------
    user = mongo.db.users.find_one({"_id": ObjectId(request.user["user_id"])})

    send_email(
        user["email"],
        "E-Waste Item Added",
        f"""
        <h2>Your Item Has Been Added</h2>
        <p><b>Item:</b> {item['itemName']}</p>
        <p><b>Category:</b> {item['category']}</p>
        <p>Thank you for using E-Waste Tracker!</p>
        """
    )

    return {"message": "Item added successfully"}, 201


# ============================================================
# REQUEST PICKUP PAGE (HTML)
# ============================================================
@user_bp.route("/request-pickup-page", methods=["GET"])
def request_pickup_page():
    return render_template("request_pickup.html")


# ============================================================
# REQUEST PICKUP API + EMAIL
# ============================================================
@user_bp.route("/request-pickup", methods=["POST"])
@jwt_required
def request_pickup():
    data = request.json

    req = {
        "user_id": request.user["user_id"],
        "item_id": data.get("item_id"),
        "address": data.get("address"),
        "date": data.get("date"),
        "status": "Pending",
        "recycler_id": None
    }

    mongo.db.requests.insert_one(req)

    user = mongo.db.users.find_one({"_id": ObjectId(request.user["user_id"])})

    # EMAIL TRIGGER
    send_email(
        user["email"],
        "Pickup Request Submitted",
        f"""
        <h2>Your Pickup Request is Submitted</h2>
        <p><b>Date:</b> {req['date']}</p>
        <p><b>Address:</b> {req['address']}</p>
        <p>We will assign a recycler soon.</p>
        """
    )

    return {"message": "Pickup request submitted"}, 201


# ============================================================
# VIEW ITEMS PAGE (HTML)
# ============================================================
@user_bp.route("/my-items-page", methods=["GET"])
def my_items_page():
    return render_template("view_items.html")


# ============================================================
# VIEW ITEMS API
# ============================================================
@user_bp.route("/my-items", methods=["GET"])
@jwt_required
def my_items():
    items = list(mongo.db.items.find({"user_id": request.user["user_id"]}))
    for i in items:
        i["_id"] = str(i["_id"])
    return {"items": items}, 200


# ============================================================
# VIEW REQUESTS PAGE
# ============================================================
@user_bp.route("/my-requests-page", methods=["GET"])
def my_requests_page():
    return render_template("view_requests.html")


# ============================================================
# VIEW REQUESTS API
# ============================================================
@user_bp.route("/my-requests", methods=["GET"])
@jwt_required
def my_requests():
    reqs = list(mongo.db.requests.find({"user_id": request.user["user_id"]}))
    for r in reqs:
        r["_id"] = str(r["_id"])
    return {"requests": reqs}, 200


# ============================================================
# FEEDBACK PAGE
# ============================================================
@user_bp.route("/feedback-page", methods=["GET"])
def feedback_page():
    return render_template("feedback.html")


# ============================================================
# FEEDBACK API
# ============================================================
@user_bp.route("/feedback", methods=["POST"])
@jwt_required
def feedback():
    data = request.json

    fb = {
        "user_id": request.user["user_id"],
        "recycler_id": data.get("recycler_id"),
        "comments": data.get("comments"),
        "rating": data.get("rating")
    }

    mongo.db.feedback.insert_one(fb)
    return {"message": "Feedback submitted"}, 201
