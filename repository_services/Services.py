from config.database import users_collection, candidates_collection
from models.users import User
from models.candidates import Candidate, UpdateCandidate
from schema.schemas import user_list_serializer, candidate_list_serializer, candidate_indvidual_serializer
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import re
from fastapi import Query


class UserService:

    # get all the Users
    @staticmethod
    def get_users():
        users = user_list_serializer(users_collection.find())
        return users

    # add User
    @staticmethod
    def add_user(user: User):
        try:
            result = users_collection.insert_one(user.model_dump())
            return {"success": True, "message": "user added successfully!", "_id": str(result.inserted_id)}
        except DuplicateKeyError as e:
            key = None
            if e.details and "keyPattern" in e.details:
                key = list(e.details["keyPattern"].keys())[0]
            return {
                "success": False,
                "message": f"User with this {key} already exists." if key else "Duplicate key error."
            }
        except Exception as e:
            return {"success": False, "message": f"Something went wrong: {str(e)}"}
    
    # get user by UUID
    @staticmethod
    def get_user_by_uuid(uuid: str):
        user = users_collection.find_one({"UUID": uuid})
        return user
        

class CandidateServices:

    # get all candidates
    @staticmethod
    def get_candidates():
        candidates = candidate_list_serializer(candidates_collection.find())
        return candidates
    
    # get a candidate by ID
    @staticmethod
    def get_candidate_by_id(id: str):
        try:
            candidate = candidates_collection.find_one({"_id": ObjectId(id)})
            return candidate
        except Exception as e:
            raise ValueError(f"Invalid candidate ID: {e}")

    # add a new candidate : unique fields email, UUID
    @staticmethod
    def add_candidate(candidate: Candidate):
        try:
            result = candidates_collection.insert_one(candidate.model_dump())
            return {"success": True, "message": "Candidate added successfully!", "_id": str(result.inserted_id)}
        except DuplicateKeyError as e:
            key = None
            if e.details and "keyPattern" in e.details:
                key = list(e.details["keyPattern"].keys())[0]
            return {
                "success": False,
                "message": f"Candidate with this {key} already exists." if key else "Duplicate key error."
            }
        except Exception as e:
            return {"success": False, "message": f"Something went wrong: {str(e)}"}
    
    # update a candidate propoint: only provide the field you want to update
    @staticmethod
    def update_candidate(id: str, candidate: UpdateCandidate):
        try:
            _id = ObjectId(id)
            candidate_data = candidate.model_dump()
            candidate_data = {k: v for k, v in candidate_data.items() if v is not None}
            if not candidate_data:
                return {"success": False, "message": "No valid fields to update."}
            result = candidates_collection.update_one({"_id": _id}, {"$set": candidate_data})
            if result.matched_count == 0:
                return {"success": False, "message": "Candidate not found."}
            return {"success": True, "message": "Candidate was updated successfully!"}
        except DuplicateKeyError as e:
            key = None
            if e.details and "keyPattern" in e.details:
                key = list(e.details["keyPattern"].keys())[0]
            return {
                "success": False,
                "message": f"Candidate with this {key} already exists." if key else "Duplicate key error."
            }
        except Exception as e:
            return {"success": False, "message": f"Something went wrong: {str(e)}"}

    # delete a candidate based on ID
    @staticmethod
    def delete_candidate(id: str):
        try:
            _id = ObjectId(id)
            result = candidates_collection.delete_one({"_id": _id})
            if result.deleted_count == 0:
                return {"success": False, "message": "Candidate not found."}
            return {"success": True, "message": "Candidate deleted successfully!"}
        except Exception as e:
            return {"success": False, "message": f"Something went wrong: {str(e)}"}

    # method for searching candidates from a single query on all fields 
    @staticmethod
    def search_candidate(query: str = Query(...)):
        escaped = re.escape(query)

        try:
            numeric_query = float(query)
        except ValueError:
            numeric_query = None

        conditions = [
            {"uuid": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"first_name": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"last_name": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"email": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"career_level": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"job_major": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"degree_type": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"nationality": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"city": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"gender": {"$regex": f".*{escaped}.*", "$options": "i"}},
            {"skills": {"$elemMatch": {"$regex": f".*{escaped}.*", "$options": "i"}}}
        ]

        if numeric_query is not None:
            conditions.append({"years_of_experience": numeric_query})
            conditions.append({"salary": numeric_query})

        results = candidates_collection.find({"$or": conditions})
        results = candidate_list_serializer(results)
        return results if results else {"message": "No Record Founded!"}
