from flask import Blueprint, request, render_template
from bson.objectid import ObjectId
from app import mongo
from app.utils import jwt_required
from app.services.email_service import send_email_html

# ✅ Define Blueprint FIRST (VERY IMPORTANT)
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ============================================================
# PAGE ROUTES (NO TOKEN REQUIRED)
# ============================================================

@admin_bp.route("/dashboard", methods=["GET"])
def admin_dashboard_page():
    return render_template("admin_dashboard.html")


@admin_bp.route("/add-recycler-page", methods=["GET"])
def add_recycler_page():
    return render_template("add_recycler.html")


@admin_bp.route("/users-page", methods=["GET"])
def users_page():
    return render_template("admin_users.html")


@admin_bp.route("/recyclers-page", methods=["GET"])
def recyclers_page():
    return render_template("admin_recyclers.html")


@admin_bp.route("/requests-page", methods=["GET"])
def requests_page():
    return render_template("admin_requests.html")


@admin_bp.route("/assign-page", methods=["GET"])
def admin_assign_page():
    return render_template("admin_assign_recycler.html")


# ============================================================
# ADMIN CHECK
# ============================================================

def admin_only():
    if request.user["role"] != "admin":
        return {"error": "Unauthorized - Admin access only"}, 403


# ============================================================
# DASHBOARD DATA API
# ============================================================

@admin_bp.route("/dashboard-data", methods=["GET"])
@jwt_required
def admin_dashboard_data():
    unauthorized = admin_only()
    if unauthorized:
        return unauthorized

    total_users = mongo.db.users.count_documents({"role": "user"})
    total_recyclers = mongo.db.users.count_documents({"role": "recycler"})
    total_requests = mongo.db.requests.count_documents({})
    pending_requests = mongo.db.requests.count_documents({"status": "Pending"})
    completed_requests = mongo.db.requests.count_documents({"status": "Completed"})

    return {
        "total_users": total_users,
        "total_recyclers": total_recyclers,
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "completed_requests": completed_requests
    }, 200


# ============================================================
# USERS LIST
# ============================================================

@admin_bp.route("/users", methods=["GET"])
@jwt_required
def get_users():
    unauthorized = admin_only()
    if unauthorized:
        return unauthorized

    users = list(mongo.db.users.find({"role": "user"}))
    for u in users:
        u["_id"] = str(u["_id"])

    return {"users": users}, 200


# ============================================================
# RECYCLERS LIST
# ============================================================

@admin_bp.route("/recyclers", methods=["GET"])
@jwt_required
def get_recyclers():
    unauthorized = admin_only()
    if unauthorized:
        return unauthorized

    recyclers = list(mongo.db.users.find({"role": "recycler"}))
    for r in recyclers:
        r["_id"] = str(r["_id"])

    return {"recyclers": recyclers}, 200


# ============================================================
# ADD RECYCLER
# ============================================================

@admin_bp.route("/add-recycler", methods=["POST"])
@jwt_required
def add_recycler():
    unauthorized = admin_only()
    if unauthorized:
        return unauthorized

    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if mongo.db.users.find_one({"email": email}):
        return {"error": "Email already exists"}, 400

    mongo.db.users.insert_one({
        "name": name,
        "email": email,
        "password": password,  # you can hash password here if needed
        "role": "recycler"
    })

    return {"message": "Recycler added successfully"}, 201


# ============================================================
# GET ALL REQUESTS
# ============================================================

@admin_bp.route("/requests", methods=["GET"])
@jwt_required
def get_requests():
    unauthorized = admin_only()
    if unauthorized:
        return unauthorized

    reqs = list(mongo.db.requests.find({}))
    for r in reqs:
        r["_id"] = str(r["_id"])

    return {"requests": reqs}, 200


# ============================================================
# FEEDBACK
# ============================================================

@admin_bp.route("/feedback", methods=["GET"])
@jwt_required
def view_feedback():
    unauthorized = admin_only()
    if unauthorized:
        return unauthorized

    feedbacks = list(mongo.db.feedback.find({}))
    for f in feedbacks:
        f["_id"] = str(f["_id"])

    return {"feedbacks": feedbacks}, 200


# ============================================================
# ASSIGN RECYCLER → SEND EMAIL TO RECYCLER
# ============================================================

@admin_bp.route("/assign-recycler", methods=["POST"])
@jwt_required
def assign_recycler():
    unauthorized = admin_only()
    if unauthorized:
        return unauthorized

    data = request.json
    request_id = data.get("request_id")
    recycler_id = data.get("recycler_id")

    # Get data
    req = mongo.db.requests.find_one({"_id": ObjectId(request_id)})
    recycler = mongo.db.users.find_one({"_id": ObjectId(recycler_id)})
    user = mongo.db.users.find_one({"_id": ObjectId(req["user_id"])})
    item = mongo.db.items.find_one({"_id": ObjectId(req["item_id"])})

    # Update request
    mongo.db.requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"recycler_id": recycler_id, "status": "Assigned"}}
    )

    # EMAIL TO RECYCLER
    send_email_html(
        recycler["email"],
        "New Pickup Assigned",
        "assigned_recycler.html",
        {
            "recycler_name": recycler["name"],
            "user_name": user["name"],
            "item_name": item["itemName"],
            "address": req["address"],
            "date": req["date"]
        }
    )

    return {"message": "Recycler Assigned & Email Sent"}, 200