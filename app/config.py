import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Secret Key
    SECRET_KEY = os.getenv("SECRET_KEY")

    # MongoDB Atlas Connection
    MONGO_URI = os.getenv("MONGO_URI")

    # JWT Authentication
    JWT_SECRET = os.getenv("JWT_SECRET")
    JWT_ALGO = os.getenv("JWT_ALGO", "HS256")

    # Email Notification System (Gmail App Password)
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
