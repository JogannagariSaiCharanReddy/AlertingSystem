from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.services import models
from api.services.database import engine
from api.routes import alerts, users ,user_management,team_management,analytics

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Enhanced Alerting and Notification Platform API",
    description="A scalable API for managing alerts with fine-grained visibility and user preferences.",
    version="1.0.0",
)

# For local development with Streamlit's default port, this is what you need.
origins = [
    "http://localhost:8501", # Streamlit default port
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"],    # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allows all headers
)


# routers
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(users.router)
app.include_router(user_management.router)
app.include_router(team_management.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Alerting Platform API"}