# Point d'entrée FASTAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import products, orders, waitlist, payments

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

@app.get("/")
def healthcheck():
    return {"status": "ok", "app": "elysian-unity-api"}

# optionnel, pour éviter le spam 404 de favicon
@app.get("/favicon.ico")
def favicon():
    return JSONResponse(content={}, status_code=204)


app.include_router(products.router)
app.include_router(orders.router)
app.include_router(waitlist.router)
app.include_router(payments.router)
