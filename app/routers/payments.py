from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import stripe

from ..database import SessionLocal
from .. import schemas, crud, models
from ..config import stripe, STRIPE_WEBHOOK_SECRET

router = APIRouter(tags=["payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create-payment-intent")
async def create_payment_intent(payload: schemas.PaymentIntentCreate, db: Session = Depends(get_db)):
    # 1) créer la commande interne + calculer le total sécurisé
    try:
        order, total = crud.create_order_from_cart(
            db=db,
            email=payload.customer.email,
            items_raw=payload.cart,
            is_student=payload.is_student,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if total <= 0:
        raise HTTPException(status_code=400, detail="Montant total invalide")

    # 2) créer le PaymentIntent Stripe
    try:
        intent = stripe.PaymentIntent.create(
            amount=total,        # total en centimes
            currency="eur",
            metadata={
                "order_id": str(order.id),
                "customer_email": payload.customer.email,
            },
            receipt_email=payload.customer.email,
            description=f"Elysian Unity — commande #{order.id}",
        )
    except Exception as e:
        # si Stripe échoue → on marque la commande étant annulée
        order.status = "cancelled"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Erreur Stripe : {e}")

    return {"clientSecret": intent.client_secret}


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Payload invalide"})
    except stripe.error.SignatureVerificationError:
        return JSONResponse(status_code=400, content={"detail": "Signature invalide"})

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        order_id = intent["metadata"].get("order_id")
        if order_id:
            order = db.query(models.Order).filter(models.Order.id == int(order_id)).first()
            if order:
                order.status = "paid"
                db.commit()

    elif event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        order_id = intent["metadata"].get("order_id")
        if order_id:
            order = db.query(models.Order).filter(models.Order.id == int(order_id)).first()
            if order:
                order.status = "cancelled"
                db.commit()

    return {"received": True}
