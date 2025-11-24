from app import mongo
from bson.objectid import ObjectId

class RecyclerModel:

    @staticmethod
    def create_recycler(name, email, password):
        recycler = {
            "name": name,
            "email": email,
            "password": password,
            "role": "recycler"
        }
        return mongo.db.users.insert_one(recycler)

    @staticmethod
    def get_recycler_by_id(recycler_id):
        return mongo.db.users.find_one({"_id": ObjectId(recycler_id)})

    @staticmethod
    def get_all_recyclers():
        return list(mongo.db.users.find({"role": "recycler"}))
