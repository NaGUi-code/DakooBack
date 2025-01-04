import random
import requests
import json
import sys

DOKAA_BASE_URL = "https://dokaa-api-sgk5mmvb3a-ew.a.run.app"


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def wheel_data(shop_id):
    url = f"{DOKAA_BASE_URL}/wheels/randomWheels/{shop_id}"
    userSeed = "1" + str(random.randint(10**14, (10**15) - 1))

    payload = json.dumps({"uuid": userSeed})
    r = requests.request("POST", url, data=payload)
    if r.status_code != 200:
        print("Error: ", r.status_code)
        return None, userSeed

    wheel_data_json = r.json()
    return wheel_data_json, userSeed


def win_wheel(wheelId, wheelHistoryId, shopId, mail, phone, userSeed, gift_name):
    url = f"{DOKAA_BASE_URL}/wheels-history/{wheelHistoryId}"

    if not mail:
        user = {"phone": phone}
    elif not phone:
        user = {"mail": mail}
    else:
        user = {"mail": mail, "phone": phone}

    payload = json.dumps(
        {
            "shopId": shopId,
            "wheelId": wheelId,
            "user": user,
            "wheelCtaType": "google",
            "marketing": False,
            "userSeed": userSeed,
            "gift": {"name": gift_name, "discountType": "fixed_cart"},
        }
    )

    headers = {
        "content-type": "application/json",
        "cookie": f"id={userSeed}",
    }

    r = requests.request("POST", url, headers=headers, data=payload)

    if r.status_code == 403:
        error_message = r.json()
        print(f"{bcolors.FAIL}Error: {error_message['message']}{bcolors.ENDC}")
        return None

    if r.status_code != 200:
        print(f"{bcolors.FAIL}Error: {r.status_code}{bcolors.ENDC}")
        return None

    wheel_data_json = r.json()
    return wheel_data_json["_id"]


def redeemPromo(giftId, shopCode):
    url = f"{DOKAA_BASE_URL}/wheels-history/{giftId}/claim-gift"

    payload = json.dumps({"shopCode": shopCode})
    random_number = "1" + str(random.randint(10**14, (10**15) - 1))

    headers = {
        "content-type": "application/json",
        "cookie": f"id={random_number}",
    }
    r = requests.request("PUT", url, data=payload, headers=headers)

    if r.status_code != 200:
        print("Error: ", r.status_code)
        print(r.text)
        return None

    return r.json()


if __name__ == "__main__":
    print(f"----- {bcolors.OKCYAN}Eat Sushi gift free{bcolors.ENDC} -----")
    shop_qr_code = input(
        f"{bcolors.OKGREEN}Enter the Eat Sushi QR Code : {bcolors.ENDC}"
    )

    if not shop_qr_code:
        print(f"{bcolors.FAIL}Invalid QR Code{bcolors.ENDC}")
        exit()

    data, userSeed = wheel_data(shop_qr_code)
    offers = data["wheel"]["offers"]
    shopName = data.get("wheel", {}).get("shopId", {}).get("name", "")
    print(f"\n{bcolors.OKCYAN}SHOP : {shopName}{bcolors.ENDC}")

    print(f"\n\n{bcolors.OKCYAN}Gifts available{bcolors.ENDC}:")
    for x, of in enumerate(offers):
        print(
            bcolors.WARNING
            + f"[{x+1}]  "
            + bcolors.ENDC
            + bcolors.HEADER
            + of["name"]
            + bcolors.ENDC
            + bcolors.OKGREEN
            + f" ({of['weight']}%)"
            + bcolors.ENDC
        )

    gift_number = input(f"{bcolors.OKGREEN}Enter the gift number : {bcolors.ENDC}")
    if not gift_number:
        print(f"{bcolors.FAIL}Invalid gift number{bcolors.ENDC}")
        exit()

    try:
        gift_number = int(gift_number)
    except ValueError:
        print(f"{bcolors.FAIL}Invalid gift number{bcolors.ENDC}")
        exit()

    if int(gift_number) - 1 not in range(len(offers)):
        print(f"{bcolors.FAIL}Invalid gift number{bcolors.ENDC}")
        exit()

    if gift_number > len(offers):
        print(f"{bcolors.FAIL}Invalid gift number{bcolors.ENDC}")
        exit()

    gift_name = offers[gift_number - 1]["name"]

    print(
        f"{bcolors.OKCYAN}You have selected {bcolors.WARNING}{gift_name}{bcolors.ENDC}{bcolors.ENDC}"
    )

    wheelCampaignField = data["wheel"]["wheelCampaignField"]
    email = ""
    phone = ""

    if wheelCampaignField.get("mail", False):
        email = input(f"{bcolors.OKGREEN}Enter your email : {bcolors.ENDC}")

    if wheelCampaignField.get("phone", False):
        phone = input(
            f"{bcolors.OKGREEN}Enter your phone number (minimum 10 chars) : {bcolors.ENDC}"
        )

    validation = input(
        f"{bcolors.OKCYAN}Are you sure you want to redeem the gift? (y/n) : {bcolors.ENDC}"
    )
    if validation.lower() != "y":
        print(f"{bcolors.FAIL}Gift redemption cancelled{bcolors.ENDC}")
        exit()

    giftId = win_wheel(
        data["wheel"]["_id"],
        data["wheelHistoryId"],
        data["wheel"]["shopId"]["_id"],
        email,
        phone,
        userSeed,
        gift_name,
    )

    if giftId:
        print(f"{bcolors.OKGREEN}Gift redeemed successfully {gift_name}{bcolors.ENDC}")
        print(
            f"{bcolors.OKCYAN}Gift link{bcolors.ENDC}: {bcolors.FAIL}https://app.dokaa.app/claim-gift?gift={giftId}{bcolors.ENDC}"
        )
        print(
            f"{bcolors.OKCYAN}Gift code{bcolors.ENDC}: {bcolors.FAIL}{giftId}{bcolors.ENDC}"
        )
        print(
            f"{bcolors.OKCYAN}Available {bcolors.ENDC}: {bcolors.FAIL}tomorrow{bcolors.ENDC}"
        )

    else:
        print(f"{bcolors.FAIL}Error redeeming gift{bcolors.ENDC}")
