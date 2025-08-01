import fastapi

# import auth router
import routers.auth as auth_router
from fastapi.middleware.cors import CORSMiddleware


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
    ],  # Add frontend URL when in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def print_request(request: fastapi.Request, call_next):
    print("CORS middleware active, origin:", request.headers.get("origin"))
    response = await call_next(request)
    return response


app.include_router(auth_router.router)


@app.get("/auth")
def root():
    return {
        "message": "You have reached the Authentication Portal. If you are seeing this, contact a developer"
    }
