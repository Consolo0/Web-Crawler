from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.Routes import router
from src.api.Middleware.ErrorMiddleware import ErrorMiddleware

app = FastAPI(
    title="Web Crawler API",
    version="1.0.0"
)

app.add_middleware(ErrorMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["crawler"])

@app.get("/")
async def root():
    return {"message": "Web Crawler API is running"}
