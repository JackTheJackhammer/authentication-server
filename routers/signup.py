from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from database import queryDatabase
from fastapi import APIRouter

router = APIRouter()


class SignUpFields(BaseModel):
    Email: str
    Name: str
    UserName: str
    Password: str


@router.post("/auth/signup")
async def signup(request: SignUpFields):
    # First Check if User doesnt already exist
    q = queryDatabase("SELECT * FROM users WHERE usrname = %s", (request.UserName))
    if q is not None:
        HTTPException(500, detail="")
    if len(q) > 0:
        HTTPException(500)

    # Ok, now check if we should allow them to sign up.
