from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI()

origins = [
    "http://localhost:5173",  # your Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://www.nameurcloud.com",
    "https://www.nameurcloud.com",
    "http://api.nameurcloud.com",
    "https://api.nameurcloud.com"
    # Add your production frontend domain here later
]
# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # for testing
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Allow POST and OPTIONS
    allow_headers=["Authorization", "Content-Type"],  # Allow these headers
)



app.include_router(router) 
