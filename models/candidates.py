from .users import User
from enum import Enum

from pydantic import EmailStr, field_validator, BaseModel
from typing import Optional

# Gender for only Option to set correct
class Gender(str, Enum):
    male = "Male"
    female = "Female"
    not_specified = "Not Specified"

# pydantic model for Candidate
class Candidate(User):
    career_level: str
    job_major: str
    years_of_experience: int
    degree_type: str
    skills: list[str]
    nationality: str
    city: str
    salary: float
    gender: Gender = Gender.not_specified

# very usefull for updating candidate only provide fields that you want to update
class UpdateCandidate(BaseModel):
    uuid: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None

    career_level: Optional[str] = None
    job_major: Optional[str] = None
    years_of_experience: Optional[int] = None
    degree_type: Optional[str] = None
    skills: Optional[list[str]] = None
    nationality: Optional[str] = None
    city: Optional[str] = None
    salary: Optional[float] = None
    gender: Optional[Gender] = None

    @field_validator("email", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        return v or None
