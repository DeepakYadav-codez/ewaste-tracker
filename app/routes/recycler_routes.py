from flask import Blueprint, request, render_template
from bson import ObjectId
from app import mongo
from app.utils import jwt_required
from app.services.email_service import send_email_html

recycler_bp = Blueprint("recycler", __name__, url_prefix="/recycler")


# -------------------------
# 1️⃣ RECYCLER DASHBOARD (HTML)
# -------------------------
@recycler_bp.route("/dashboard", methods=["GET"])
def recycler_dashboard_page():
    return render_template("recycler_dashboard.html")


# -------------------------
# 2️⃣ PENDING REQUESTS PAGE
# -------------------------
@recycler_bp.route("/pending", methods=["GET"])
def pending_page():
    return render_template("recycler_pending.html")


# -------------------------
# 3️⃣ ASSIGNED REQUESTS PAGE
# -------------------------
@recycler_bp.route("/assigned", methods=["GET"])
def assigned_page():
    return render_template("recycler_assigned.html")


# -------------------------
# 4️⃣ API – GET PENDING REQUESTS
# -------------------------
@recycler_bp.route("/pending-data", methods=["GET"])
@jwt_required
def pending_data():
    recycler_id = request.user["user_id"]

    reqs = list(mongo.db.requests.find({
        "recycler_id": recycler_id,
        "status": "Assigned"
    }))

    for r in reqs:
        r["_id"] = str(r["_id"])
        r["item_id"] = str(r["item_id"])
        r["user_id"] = str(r["user_id"])

    return {"pending": reqs}, 200


# -------------------------
# 5️⃣ API – GET ASSIGNED REQUESTS
# -------------------------
@recycler_bp.route("/assigned-data", methods=["GET"])
@jwt_required
def assigned_data():
    recycler_id = request.user["user_id"]

    reqs = list(mongo.db.requests.find({
        "recycler_id": recycler_id,
        "status": "Accepted"
    }))

    for r in reqs:
        r["_id"] = str(r["_id"])
        r["item_id"] = str(r["item_id"])
        r["user_id"] = str(r["user_id"])

    return {"assigned": reqs}, 200


# -------------------------
# 6️⃣ ACCEPT REQUEST
# -------------------------
@recycler_bp.route("/accept-request", methods=["POST"])
@jwt_required
def accept_request():
    data = request.json
    request_id = data.get("request_id")

    req = mongo.db.requests.find_one({"_id": ObjectId(request_id)})
    if not req:
        return {"error": "Request not found"}, 404

    user = mongo.db.users.find_one({"_id": ObjectId(req["user_id"])})
    item = mongo.db.items.find_one({"_id": ObjectId(req["item_id"])})

    mongo.db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": "Accepted"}}
    )

    send_email_html(
        user["email"],
        "Pickup Accepted",
        "recycler_accept_email.html",
        {
            "user_name": user["name"],
            "item_name": item["itemName"],
            "date": req["date"],
            "address": req["address"]
        }
    )

    return {"message": "Request Accepted"}, 200


# -------------------------
# 7️⃣ COMPLETE REQUEST
# -------------------------
@recycler_bp.route("/complete-request", methods=["POST"])
@jwt_required
def complete_request():
    data = request.json
    request_id = data.get("request_id")

    req = mongo.db.requests.find_one({"_id": ObjectId(request_id)})
    if not req:
        return {"error": "Request not found"}, 404

    user = mongo.db.users.find_one({"_id": ObjectId(req["user_id"])})
    item = mongo.db.items.find_one({"_id": ObjectId(req["item_id"])})

    mongo.db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": "Completed"}}
    )

    send_email_html(
        user["email"],
        "Pickup Completed",
        "recycler_complete_email.html",
        {
            "user_name": user["name"],
            "item_name": item["itemName"]
        }
    )

    send_email_html(
        "admin@gmail.com",
        "Pickup Completed",
        "recycler_complete_email.html",
        {
            "user_name": user["name"],
            "item_name": item["itemName"]
        }
    )

    return {"message": "Request Completed"}, 200