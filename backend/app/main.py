
import os
from fastapi import FastAPI
from . import routes
from .database import init_db
from .rate_limiter import limiter_middleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoTestAI API")

@app.on_event("startup")
async def startup():
    await init_db()

# CORS setup
allowed = os.getenv("ALLOWED_ORIGINS", "*")
if allowed and allowed != "*":
    origins = [o.strip() for o in allowed.split(",")]
else:
    origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter middleware (redis-backed)
app.middleware("http")(limiter_middleware)

app.include_router(routes.router, prefix="/api")
