from fastapi import FastAPI
from app.api.routes import router


# Create FastAPI app
app = FastAPI()

# Include your routes
app.include_router(router)