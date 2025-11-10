# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from inventor_api import get_fx_parameters

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/parameters")
def read_parameters():
    return get_fx_parameters()