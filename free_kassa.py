import hashlib
from urllib.parse import urlencode
from config import FREE_KASSA_MERCHANT_ID, FREE_KASSA_SECRET1, FREE_KASSA_SECRET2

def generate_payment_url(order_id, amount, description, user_id):
    signature_str = f"{FREE_KASSA_MERCHANT_ID}:{amount}:{order_id}:{FREE_KASSA_SECRET1}"
    signature = hashlib.md5(signature_str.encode('utf-8')).hexdigest()

    params = {
        "m": FREE_KASSA_MERCHANT_ID,
        "oa": amount,
        "o": order_id,
        "s": signature,
        "i": user_id,
        "us_desc": description,
        "us_id": user_id,
        "email": "",
        "phone": "",
        "lang": "ru"
    }
    base_url = "https://www.free-kassa.ru/merchant/cash.php"
    return f"{base_url}?{urlencode(params)}"

def check_signature(params):
    sign = params.get("SIGN")
    out_summ = params.get("OutSum")
    inv_id = params.get("InvId")

    sign_str = f"{out_summ}:{inv_id}:{FREE_KASSA_SECRET2}"
    sign_check = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    return sign.lower() == sign_check.lower()
