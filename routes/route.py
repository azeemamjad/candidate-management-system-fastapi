from fastapi import APIRouter, HTTPException, Request
from models.users import User
from models.candidates import Candidate, UpdateCandidate
from repository_services.Services import UserService, CandidateServices
from config.database import client
from functools import wraps
from schema.schemas import candidate_indvidual_serializer
import re, os
from fastapi.responses import JSONResponse, FileResponse
import csv

router = APIRouter()

# for checking if the server is running and databse is connected!
@router.get('/health')
async def health_check():
    return {"message": "The Server is running!", "database": "connected!" if client.admin.command("ping") else "disconnected"}

@router.get("/users")
async def get_users():
    return JSONResponse(
        status_code=200,
        content=UserService.get_users()
    )

@router.post("/users/add/")
async def add_user(user: User):
    result = UserService.add_user(user)
    if result["success"]:
        return JSONResponse(
            status_code=201,  # ✅ Custom status code
            content={
                "message": result["message"],
                "user": user.model_dump(),
                "_id": result.get("_id")
            }
        )
    else:
        raise HTTPException(status_code=400, detail=result["message"])

# dacorator for security layer on the route of candidates.
def require_uuid(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request =  kwargs.get("request", "")
        if request:
            uuid = request.headers.get("X-USER-UUID", "")
            if uuid:
                user = UserService.get_user_by_uuid(uuid)
                if user:
                    return await func(*args, **kwargs)
                else:
                    raise HTTPException(status_code=400, detail="Your X-USER-UUID not found!")
            else:
                raise HTTPException(status_code=400, detail="'X-USER-UUID' is missing from the header")
        else:
            raise HTTPException(status_code=404, detail="Request Not Found!")
    return wrapper

# list all the candidates
@router.get("/candidates")
@require_uuid
async def get_candidates(request: Request):
    return CandidateServices.get_candidates()

# add a new candidate
@router.post("/candidates/add/")
@require_uuid
async def add_candidate(candidate: Candidate, request: Request):
    result = CandidateServices.add_candidate(candidate)
    if result["success"]:
        return JSONResponse(
            status_code=201,
            content={
                "message": result["message"],
                "user": candidate.model_dump(),
                "_id": result.get("_id")
            })
    else:
        raise HTTPException(status_code=400, detail=result["message"])

# update a candidate by it's id
@router.post("/candidates/update/{id}/")
@require_uuid
async def update_candidate(id: str, candidate: UpdateCandidate, request: Request):
    updated = CandidateServices.update_candidate(id, candidate)
    if updated["success"]:
       candidate = CandidateServices.get_candidate_by_id(id)
       return {
           "message": updated["message"],
            "user": candidate_indvidual_serializer(candidate),
            "_id": updated.get("_id")
       }
    else:
        raise HTTPException(status_code=400, detail=updated["message"])

# delete a candidate
@router.delete("/candidates/delete/{id}/")
@require_uuid
async def delete_candidate(id: str, request: Request):
    deleted = CandidateServices.delete_candidate(id)
    if deleted['success']:
        return {
           "message": deleted["message"],
            "_id": id
       }
    else:
        raise HTTPException(status_code=400, detail=deleted["message"])
    
# search a candidate by all fields
@router.get("/candidates/search/{query}")
@require_uuid
async def search_candidates(query: str, request: Request):
    results = CandidateServices.search_candidate(query)
    if results:
        return {"results": results}
    else:
        return {"message": "No Record Founded!"}

REPORT_PATH = "reports/report.csv"
@router.post("/generate-report")
@require_uuid
async def generate_report(request: Request):
    os.makedirs("reports", exist_ok=True)
    rows = CandidateServices.get_candidates()
    if not rows:
        return JSONResponse(status_code=404, content={"detail": "No candidates found."})
    with open(REPORT_PATH, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return JSONResponse(
        status_code=200,
        content={
            "message": "Report Generated Successfully!",
            "download url": "/download-report"
        })

@router.get("/download-report")
@require_uuid
async def download_report(request: Request):
    return FileResponse(REPORT_PATH, media_type="text/csv", filename="candidates_report", status_code=200)