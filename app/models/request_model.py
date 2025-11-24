from app import mongo
from bson.objectid import ObjectId

class RequestModel:

    @staticmethod
    def create_request(user_id, item_id, address, date):
        req = {
            "user_id": user_id,
            "item_id": item_id,
            "address": address,
            "date": date,
            "status": "Pending",
            "recycler_id": None
        }
        return mongo.db.requests.insert_one(req)

    @staticmethod
    def get_request_by_id(request_id):
        return mongo.db.requests.find_one({"_id": ObjectId(request_id)})

    @staticmethod
    def get_requests_by_user(user_id):
        return list(mongo.db.requests.find({"user_id": user_id}))

    @staticmethod
    def get_pending_requests():
        return list(mongo.db.requests.find({"status": "Pending"}))

    @staticmethod
    def assign_recycler(request_id, recycler_id):
        return mongo.db.requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"recycler_id": recycler_id, "status": "Accepted"}}
        )

    @staticmethod
    def complete_request(request_id):
        return mongo.db.requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "Completed"}}
        )

    @staticmethod
    def get_requests_assigned_to_recycler(recycler_id):
        return list(mongo.db.requests.find({"recycler_id": recycler_id}))
