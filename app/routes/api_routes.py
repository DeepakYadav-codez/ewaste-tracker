from flask import Blueprint, request
from app.utils import jwt_required
from app import mongo
from bson.objectid import ObjectId

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ------------------ API STATUS CHECK ------------------
@api_bp.route("/status", methods=["GET"])
def status():
    return {"status": "API is running"}, 200


# ------------------ USER: My Items --------------------
@api_bp.route("/user/items", methods=["GET"])
@jwt_required
def api_user_items():
    items = list(mongo.db.items.find({"user_id": request.user["user_id"]}))
    for i in items:
        i["_id"] = str(i["_id"])
    return {"items": items}, 200


# ---------------- USER: My Requests -------------------
@api_bp.route("/user/requests", methods=["GET"])
@jwt_required
def api_user_requests():
    reqs = list(mongo.db.requests.find({"user_id": request.user["user_id"]}))
    for r in reqs:
        r["_id"] = str(r["_id"])
    return {"requests": reqs}, 200


# ---------------- RECYCLER: Pending Requests ----------
@api_bp.route("/recycler/pending", methods=["GET"])
@jwt_required
def api_recycler_pending():
    if request.user["role"] != "recycler":
        return {"error": "Unauthorized"}, 403

    pending = list(mongo.db.requests.find({"status": "Pending"}))
    for r in pending:
        r["_id"] = str(r["_id"])
    return {"pending_requests": pending}, 200


# ---------------- RECYCLER: My Requests ---------------
@api_bp.route("/recycler/my-requests", methods=["GET"])
@jwt_required
def api_recycler_my_requests():
    if request.user["role"] != "recycler":
        return {"error": "Unauthorized"}, 403

    assigned = list(mongo.db.requests.find({"recycler_id": request.user["user_id"]}))
    for r in assigned:
        r["_id"] = str(r["_id"])
    return {"assigned_requests": assigned}, 200


# ------------------ ADMIN: Analytics ------------------
@api_bp.route("/admin/analytics", methods=["GET"])
@jwt_required
def api_admin_analytics():
    if request.user["role"] != "admin":
        return {"error": "Admin access only"}, 403

    total_users = mongo.db.users.count_documents({})
    total_recyclers = mongo.db.users.count_documents({"role": "recycler"})
    total_requests = mongo.db.requests.count_documents({})
    completed = mongo.db.requests.count_documents({"status": "Completed"})
    pending = mongo.db.requests.count_documents({"status": "Pending"})

    return {
        "total_users": total_users,
        "total_recyclers": total_recyclers,
        "total_requests": total_requests,
        "completed_requests": completed,
        "pending_requests": pending
    }, 200


# ------------------ ADMIN: All Users ------------------
@api_bp.route("/admin/users", methods=["GET"])
@jwt_required
def api_admin_users():
    if request.user["role"] != "admin":
        return {"error": "Admin access only"}, 403

    users = list(mongo.db.users.find({}))
    for u in users:
        u["_id"] = str(u["_id"])
    return {"users": users}, 200
