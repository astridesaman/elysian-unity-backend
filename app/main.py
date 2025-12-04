# Point d'entrée FASTAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import products, orders, waitlist

app = FastAPI(title="Elysian Unity API")

# Autorisation du front elysianunity.fr
origins = [
    "https://elysianunity.fr"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["**"],
)

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(waitlist.router)