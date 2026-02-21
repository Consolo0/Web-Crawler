from fastapi import FastAPI
from fastapi.responses import FileResponse
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
    return {"message": "Q||__;Q_________ GOT EM HA"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")
