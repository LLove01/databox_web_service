from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database.init_db import init_db
from backend.routes import github_routes, analytics_routes, databox_routes, oauth_callback, log_routes

app = FastAPI()

init_db()  # Initialize the database

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(oauth_callback.router)
app.include_router(github_routes.router)
app.include_router(analytics_routes.router)
app.include_router(databox_routes.router)
app.include_router(log_routes.router)
