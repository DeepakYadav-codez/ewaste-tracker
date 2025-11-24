from flask import Blueprint, request, render_template
from bson.objectid import ObjectId
from app import mongo
from app.utils import jwt_required

recycler_bp = Blueprint("recycler", __name__, url_prefix="/recycler")


# ============================================================
# PAGE ROUTES (NO TOKEN REQUIRED FOR LOADING HTML)
# ============================================================

# Recycler Dashboard Page
@recycler_bp.route("/dashboard", methods=["GET"])
def recycler_dashboard_page():
    return render_template("recycler_dashboard.html")


# Pending Requests Page
@recycler_bp.route("/pending", methods=["GET"])
def recycler_pending_page():
    return render_template("recycler_pending.html")


# Assigned Requests Page
@recycler_bp.route("/assigned", methods=["GET"])
def recycler_assigned_page():
    return render_template("recycler_assigned.html")


# ============================================================
# DATA API — ROLE: RECYCLER ONLY
# ============================================================

# -------- Pending Requests Data --------
@recycler_bp.route("/pending-data", methods=["GET"])
@jwt_required
def pending_data():

    if request.user["role"] != "recycler":
        return {"error": "Unauthorized"}, 403

    pending = list(mongo.db.requests.find({"status": "Pending"}))

    for r in pending:
        r["_id"] = str(r["_id"])

    return {"pending": pending}, 200


# -------- Assigned Requests Data --------
@recycler_bp.route("/assigned-data", methods=["GET"])
@jwt_required
def assigned_data():

    if request.user["role"] != "recycler":
        return {"error": "Unauthorized"}, 403

    recycler_id = request.user["user_id"]

    assigned = list(mongo.db.requests.find({
        "status": "Assigned",
        "recycler_id": recycler_id
    }))

    for r in assigned:
        r["_id"] = str(r["_id"])

    return {"assigned": assigned}, 200


# ============================================================
# ACTION ROUTES — ACCEPT REQUEST & COMPLETE REQUEST
# ============================================================

# -------- Accept Request --------
@recycler_bp.route("/accept-request/<request_id>", methods=["PUT"])
@jwt_required
def accept_request(request_id):

    if request.user["role"] != "recycler":
        return {"error": "Unauthorized"}, 403

    recycler_id = request.user["user_id"]

    mongo.db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {
            "status": "Assigned",
            "recycler_id": recycler_id
        }}
    )

    return {"message": "Request Assigned Successfully"}, 200


# -------- Mark Request Completed --------
@recycler_bp.route("/complete-request/<request_id>", methods=["PUT"])
@jwt_required
def complete_request(request_id):

    if request.user["role"] != "recycler":
        return {"error": "Unauthorized"}, 403

    mongo.db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {
            "status": "Completed"
        }}
    )

    return {"message": "Request Marked Completed"}, 200
