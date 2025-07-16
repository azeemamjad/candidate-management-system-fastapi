import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient
from uuid import uuid4
from main import app 

client = TestClient(app) 

@pytest.fixture(autouse=True)
def clear_collections():
    db = MongoClient()["users_db_test"]
    db["users-collection"].delete_many({})
    db["candidates-collection"].delete_many({})
    yield
    db["users-collection"].delete_many({})
    db["candidates-collection"].delete_many({})

def test_health():
    response = client.get("/health")
    assert response.json()['message'] == "The Server is running!"
    assert response.json()['database'] == "connected!"
    assert response.status_code == 200

@pytest.fixture
def test_add_user():
    test_uuid = str(uuid4())
    response = client.post("/users/add", json={
        "UUID": test_uuid,
        "first_name": "Fixture",
        "last_name": "User",
        "email": f"user{uuid4().hex[:6]}@example.com"
    })
    assert response.json()['message'] == "user added successfully!"
    assert response.status_code == 201
    return test_uuid 

def test_get_candidates(test_add_user, test_add_candidate):
    response = client.get("/candidates",
                            headers={"X-USER-UUID": test_add_user})
    response.json()[0]['UUID'] == test_add_candidate
    assert response.status_code == 200

@pytest.fixture
def test_add_candidate(test_add_user):
    response = client.post("/candidates/add", json={
        "first_name": "Ahsan",
        "last_name": "Khan",
        "email": f"ahsan{uuid4().hex[:6]}@gmail.com",
        "UUID": "CD04",
        "career_level": "Civil Engineer",
        "job_major": "Tower Developer",
        "years_of_experience": 1,
        "degree_type": "Bachelor",
        "skills": ["basements", "stairs"],
        "nationality": "Pakistani",
        "city": "Vehri",
        "salary": 35000,
        "gender": "Male"
    }, headers={"X-USER-UUID": test_add_user})
    assert response.json()['message'] == "Candidate added successfully!"
    assert response.status_code == 201
    return response.json()['_id']

def test_update_candidate(test_add_candidate, test_add_user):
    response = client.post(f"/candidates/update/{test_add_candidate}/",
                           json={"first_name": "Azeem", "last_name": "Amjad"},
                           headers={"X-USER-UUID": test_add_user})
    
    assert response.json()['user']['first_name'] == "Azeem"
    assert response.json()['user']['last_name'] == "Amjad"
    assert response.json()['message'] == "Candidate was updated successfully!"
    assert response.status_code == 200

def test_delete_candidate(test_add_candidate, test_add_user):
    response = client.delete(f"/candidates/delete/{test_add_candidate}/",
                             headers={"X-USER-UUID": test_add_user})
    assert response.status_code == 200
    assert response.json()['message'] == "Candidate deleted successfully!"

def test_search_candidate(test_add_candidate, test_add_user):
    query = "Ahsan"
    response = client.get(f"/candidates/search/{query}", headers={"X-USER-UUID": test_add_user})

    response.json()['results'][0]['id'] == test_add_candidate
    response.status_code == 200