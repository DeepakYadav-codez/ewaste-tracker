import datetime
import jwt
import smtplib
from email.mime.text import MIMEText
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import Config


# =========================
# Password Hashing
# =========================
def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, hashed_password):
    return check_password_hash(hashed_password, password)


# =========================
# Create JWT Token
# =========================
def create_jwt(payload):
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return token


# =========================
# Decode JWT Token
# =========================
def decode_jwt(token):
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# =========================
# JWT Required Decorator
# =========================
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token missing"}), 401

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        decoded = decode_jwt(token)
        if not decoded:
            return jsonify({"error": "Invalid or expired token"}), 401

        request.user = decoded
        return f(*args, **kwargs)

    return decorated


# =========================
# EMAIL NOTIFICATION SYSTEM
# =========================
def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = Config.EMAIL_HOST_USER
        msg["To"] = to

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(Config.EMAIL_HOST_USER, Config.EMAIL_HOST_PASSWORD)
        server.sendmail(Config.EMAIL_HOST_USER, to, msg.as_string())
        server.quit()

        print("Email sent successfully to:", to)

    except Exception as e:
        print("Email error:", e)
