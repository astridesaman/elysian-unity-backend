import os
from dotenv import load_dotenv

import stripe

load_dotenv()

STRIPE_KEY_SECRET = os.getenv("STRIPE_KEY_SECRET")
#STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


if not STRIPE_KEY_SECRET:
    raise RuntimeError("STRIPE_KEY_SECRET manquant dans l'environnement !")


stripe.api_key = STRIPE_KEY_SECRET