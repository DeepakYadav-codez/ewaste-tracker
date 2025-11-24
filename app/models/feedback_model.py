from app import mongo
from bson.objectid import ObjectId

class FeedbackModel:

    @staticmethod
    def add_feedback(user_id, recycler_id, comments, rating):
        fb = {
            "user_id": user_id,
            "recycler_id": recycler_id,
            "comments": comments,
            "rating": rating
        }
        return mongo.db.feedback.insert_one(fb)

    @staticmethod
    def get_feedback_for_recycler(recycler_id):
        return list(mongo.db.feedback.find({"recycler_id": recycler_id}))

    @staticmethod
    def get_all_feedback():
        return list(mongo.db.feedback.find({}))
