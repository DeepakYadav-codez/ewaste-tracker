from flask import Flask
from flask import render_template
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os

mongo = PyMongo()

def create_app():
    # Load environment variables
    load_dotenv()

    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Config values
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Initialize MongoDB
    mongo.init_app(app)

    # Enable CORS (optional but good for frontend requests / future mobile app)
    CORS(app)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.recycler_routes import recycler_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(recycler_bp)
    app.register_blueprint(admin_bp)

    # Home route
    @app.route("/")
    def home():
        return render_template("index.html")

    return app
