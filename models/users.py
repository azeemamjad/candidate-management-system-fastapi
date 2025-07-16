from pydantic import BaseModel, EmailStr

# Pydantic Moadel for User
class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    UUID: str
    authorized: bool = False