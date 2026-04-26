from fastapi import FastAPI, Request
import pandas as pd
import requests

app = FastAPI()

SKU = pd.read_excel("sku_map.xlsx")
FEES = pd.read_excel("return_fees.xlsx")


def get_weight(sku):
    r = SKU[SKU["SKU"] == sku]
    return float(r.iloc[0]["weight_kg"]) if not r.empty else 1.0


def get_fee(sku):
    r = FEES[FEES["SKU"] == sku]
    return float(r.iloc[0]["shipment_fee"]) if not r.empty else 0.0


def detect(tag):
    return "FREE" if tag == "free_return" else "PAID"


@app.post("/webhook/gorgias")
async def webhook(req: Request):

    data = await req.json()

    tag = data["tag"]
    ticket_id = data["ticket_id"]
    order_id = data["order_id"]

    order = get_order(order_id)

    mode = detect(tag)

    if mode == "PAID":
        fee = sum(get_fee(i["sku"]) * i["qty"] for i in order["items"])
        msg = f"Paid return. Shipment fee: €{fee:.2f}"
    else:
        msg = "Free return approved."

    send_gorgias(ticket_id, msg)

    return {"ok": True}


def get_order(order_id):
    return {"items": [{"sku": "ABC123", "qty": 1}]}


def send_gorgias(ticket_id, msg):
    print(ticket_id, msg)