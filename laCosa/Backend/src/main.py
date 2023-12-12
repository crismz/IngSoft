from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import api_router
from partidas.mazo.cartas.models import Card
from partidas.mazo.cartas.db import db
from partidas.mazo.cartas.utils import populate_with_cards
from pony.orm import db_session

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome, cowboy!"}

app.include_router(api_router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.bind('sqlite',filename="db.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
with db_session:
    if Card.select().count() == 0:
        populate_with_cards()
