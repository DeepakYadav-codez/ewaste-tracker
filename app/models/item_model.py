from app import mongo
from bson.objectid import ObjectId

class ItemModel:

    @staticmethod
    def add_item(user_id, itemName, category, description):
        item = {
            "user_id": user_id,
            "itemName": itemName,
            "category": category,
            "description": description,
            "status": "Pending"
        }
        return mongo.db.items.insert_one(item)

    @staticmethod
    def get_items_by_user(user_id):
        return list(mongo.db.items.find({"user_id": user_id}))

    @staticmethod
    def get_item_by_id(item_id):
        return mongo.db.items.find_one({"_id": ObjectId(item_id)})
