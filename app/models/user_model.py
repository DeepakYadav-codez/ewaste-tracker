from app import mongo
from bson.objectid import ObjectId

class UserModel:

    @staticmethod
    def create_user(name, email, password, role="user"):
        user = {
            "name": name,
            "email": email,
            "password": password,
            "role": role
        }
        return mongo.db.users.insert_one(user)

    @staticmethod
    def get_user_by_email(email):
        return mongo.db.users.find_one({"email": email})

    @staticmethod
    def get_user_by_id(user_id):
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def get_all_users():
        return list(mongo.db.users.find({}))
