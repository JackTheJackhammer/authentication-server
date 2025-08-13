from fastapi import APIRouter, HTTPException, Request, Cookie
from typing import Annotated
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database import queryDatabase, modifyDatabase
from secrets import token_hex
from hashlib import sha256
from datetime import datetime, timedelta, timezone

# DEBUG SECRETS FOR AUTHENTICATION, PLEASE CHANGE IN PRODUCTION
# Make me a config file!
TIME_TO_EXPIRY = 900  # seconds

router = APIRouter()


@router.get("/auth")
def auth():
    return {"message": "Authentication endpoint reached!"}


# Login Endpoint's Response Body
class LoginCredentials(BaseModel):
    username: str
    password: str


def generateCookieSession(username: str, ip_address: str):
    # This function should generate a secure cookie session

    session_id = token_hex(32)  # Generate a random session ID
    # Log that shit

    modifyDatabase(
        """
        INSERT INTO sessions(
	token_str, usrname, login_time, expiry, ivp4)
	VALUES (%s, %s, %s, %s, %s);""",
        (
            session_id,
            username,
            datetime.now(timezone.utc),
            datetime.now(timezone.utc) + timedelta(seconds=TIME_TO_EXPIRY),
            ip_address,
        ),
    )

    return session_id


# Login Endpoint
@router.post("/auth/login")
async def login(login_credentials: LoginCredentials, request: Request):
    # Validate with Database
    # Note: The credentials should be hashed in the fucking DB. They are sent over plaintext https
    q = queryDatabase(
        """
        SELECT * FROM users WHERE usrname = %s
    """,
        (login_credentials.username,),
    )

    # Reject Wrong Credentials
    # If the query returns an empty list, it means no user was found with the provided
    if q == [] or q is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if q[0][2] != sha256(f"{login_credentials.password}{q[0][6]}".encode()).hexdigest():
        # Password does not match
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # User is probably authenticated, send a cookie session

    # switch to Secure=True, samesite="none" when in prod
    response = JSONResponse(content={"message": "User authenticated successfully!"})
    response.set_cookie(
        key="session",
        value=generateCookieSession(login_credentials.username, "PLACEHOLDER"),
        httponly=True,
        secure=False,  #  allow testing on localhost
        samesite="lax",
        expires=datetime.now(timezone.utc) + timedelta(seconds=TIME_TO_EXPIRY),
    )
    print(response.headers, response.body)
    # switch to Secure=True, samesite="none" when in prod
    return response


def CheckSessionID(ID: str):
    q = queryDatabase(
        "SELECT * FROM sessions WHERE token_str = %s AND expiry > CURRENT_TIMESTAMP AND logged_out = FALSE",
        (ID,),
    )
    if q is not None:
        if len(q) > 0:
            # Authenticated
            print(q)
            return True

    return False


# Make it such that this doesnt make a new entry if the old cookie still isnt expired or logged out
@router.get("/auth/verify/")
def checkIDEndpoint(session: Annotated[str | None, Cookie()] = None):
    if session is None:
        raise HTTPException(status_code=500)
    if not CheckSessionID(session):
        print(session)
        raise HTTPException(status_code=401)


@router.post("/auth/deauth")
def RevokeSessionID(session: Annotated[str | None, Cookie()] = None):
    # First check if the session is actually alive

    if session is None:
        raise HTTPException(status_code=500)

    if not CheckSessionID(session):
        raise HTTPException(status_code=401)

    # If so, revoke that shit

    action = modifyDatabase(
        "UPDATE sessions SET logged_out = TRUE WHERE token_str = %s", (session,)
    )

    if not action:
        raise HTTPException(status_code=500)


# should i let the user do this? is this best practice?
@router.get("/auth/getLoggedCredentials")
def GetLoggedCredentials(session: Annotated[str | None, Cookie()] = None):
    query = queryDatabase(
        "select usrname from public.sessions where token_str = %s", (session,)
    )
    if query is None:
        raise HTTPException(status_code=404)
    return query
