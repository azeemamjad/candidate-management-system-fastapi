# convert a single Candidate to Dictionary
def user_individual_serializers(user) -> dict :
    return {
        "id": str(user["_id"]),
        "first_name": user.get("first_name", ""),
        "last_name": user.get("last_name", ""),
        "email": user.get("email", "email"),
        "UUID": user.get("UUID", ""),
        "authorized": user.get("authorized", False)
    }

# convert a list of Candidates to a List Of Dictionaries
def user_list_serializer(users):
    return [user_individual_serializers(user) for user in users]

# convert a single Candidate Object to Dictionary for Response!
def candidate_indvidual_serializer(candidate) -> dict :
    return {
        "id": str(candidate["_id"]),
        "first_name": candidate.get("first_name", ""),
        "last_name": candidate.get("last_name", ""),
        "email": candidate.get("email", "email"),
        "UUID": candidate.get("UUID", ""),
        "career_level": candidate.get("career_level", ""),
        "job_major": candidate.get("job_major", ""),
        "years_of_experience": candidate.get("years_of_experience", ""),
        "degree_type": candidate.get("degree_type", ""),
        "skills": candidate.get("skills", ""),
        "nationality": candidate.get("nationality", ""),
        "city": candidate.get("city", ""),
        "salary": candidate.get("salary", ""),
        "gender": candidate.get("gender", ""),
    }

# convert list of Cantidates to list of dictionaries
def candidate_list_serializer(candidates):
    return [candidate_indvidual_serializer(candidate) for candidate in candidates]