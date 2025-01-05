import random
import os
import requests
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv(dotenv_path=".env.local")

URL_WIN_WHEEL = os.getenv("URL_WIN_WHEEL")
URL_REDDEM_PROMO = os.getenv("URL_REDDEM_PROMO")
TOKEN = os.getenv("TOKEN")

with open("eatsushi.json", "r") as f:
    eatSushiShops = json.load(f)


class RequestWinWheel(BaseModel):
    wheel_id: str
    mail: str = None
    phone: str = None
    gift_name: str
    wheelCtaType: str = "google"
    marketing: bool = False
    discountType: str = "fixed_cart"


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/list/shops")
async def root():
    return {"message": "List of shops", "data": eatSushiShops, "error": None}


@app.post("/win_wheel")
async def win_wheel(requestsWinWheel: RequestWinWheel):
    if not requestsWinWheel.mail and not requestsWinWheel.phone:
        return {"message": "Mail or phone are required", "data": None, "error": True}
    elif not requestsWinWheel.mail:
        user = {"phone": requestsWinWheel.phone}
    elif not requestsWinWheel.phone:
        user = {"mail": requestsWinWheel.mail}
    else:
        user = {"mail": requestsWinWheel.mail, "phone": requestsWinWheel.phone}

    userSeed = "1" + str(random.randint(10**14, (10**15) - 1))

    payload = {
        "wheelId": requestsWinWheel.wheel_id,
        "user": user,
        "wheelCtaType": "google",
        "marketing": False,
        "userSeed": userSeed,
        "gift": {
            "name": requestsWinWheel.gift_name,
            "discountType": requestsWinWheel.discountType,
        },
    }

    headers = {
        "content-type": "application/json",
        "cookie": f"id={userSeed}",
    }

    r = requests.request(
        "POST", URL_WIN_WHEEL, headers=headers, data=json.dumps(payload)
    )

    if r.status_code == 403:
        error_message = r.json()
        return {"message": error_message, "data": None, "error": True}, 403

    if r.status_code != 200:
        return {"message": "Error", "data": r.text, "error": True}, 500

    return {"message": "Wheel data", "data": r.json(), "error": None}, 200
