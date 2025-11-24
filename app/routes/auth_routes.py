from flask import Blueprint, request, render_template
from app import mongo
from app.utils import create_jwt, verify_password, hash_password
from bson.objectid import ObjectId

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# ===========================
#   REGISTER PAGE (GET)
# ===========================
@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")


# ===========================
#   REGISTER USER (POST)
# ===========================
@auth_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    # Check if email exists
    existing_user = mongo.db.users.find_one({"email": email})
    if existing_user:
        return {"error": "Email already exists"}, 400

    hashed_pw = hash_password(password)

    user = {
        "name": name,
        "email": email,
        "password": hashed_pw,
        "role": role
    }

    result = mongo.db.users.insert_one(user)
    user_id = str(result.inserted_id)

    token = create_jwt({"user_id": user_id, "role": role})

    return {"message": "User registered", "token": token, "role": role}, 201


# ===========================
#   LOGIN PAGE (GET)
# ===========================
@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# ===========================
#   LOGIN USER (POST)
# ===========================
@auth_bp.route("/login", methods=["POST"])
def login_user():
    data = request.json

    email = data.get("email")
    password = data.get("password")

    user = mongo.db.users.find_one({"email": email})

    if not user:
        return {"error": "Invalid email"}, 401

    # Verify password
    if not verify_password(password, user["password"]):
        return {"error": "Incorrect password"}, 401

    user_id = str(user["_id"])
    role = user["role"]

    token = create_jwt({"user_id": user_id, "role": role})

    return {
        "message": "Login successful",
        "token": token,
        "role": role
    }, 200


# ===========================
#   LOGOUT (Frontend Only)
# ===========================
@auth_bp.route("/logout", methods=["GET"])
def logout():
    # Actual logout is handled using JS (token removed from localStorage)
    return render_template("login.html")
