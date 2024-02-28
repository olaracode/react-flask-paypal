"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import base64

from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
import requests
api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)

PAYPAL_CLIENT = os.environ.get("PAYPAL_CLIENT")
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET")
PAYPAL_INTENT = "CAPTURE"
PAYPAL_APPLICATION_CONTEXT = {
    "brand_name": "Olaracode",
    "landing_page": "NO_PREFERENCE",
    "use_action": "PAY_NOW"
}


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200

@api.route("/create_order", methods=["POST"])
def create_paypal_order():

    body = request.get_json()
    items = body.get("items", None)
    if items is None:
        return APIException("MISSING FIELDS", 400, {
            "items": "The items are required to create an order"
        }).to_dict()

    total = sum(item["price"] * item["quantity"] for item in items)
    order = {
        "intent": PAYPAL_INTENT,
        "application_context": PAYPAL_APPLICATION_CONTEXT,
        "purchase_units": [
          {
            "amount": {
              "currency_code": "USD",
              "value": total,
              "breakdown": {
                  "item_total": {
                      "currency_code": "USD",
                      "value": total,
                  }
              }
            },
            "items": [
                {
                    "name": item["name"],
                    "unit_amount": {
                        "currency_code": "USD",
                        "value": item["price"]
                    },
                    "quantity": item["quantity"]
            } for item in items]
          }
        ]
      }

    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{PAYPAL_CLIENT}:{PAYPAL_SECRET}'.encode()).decode()}"
    }

    response = requests.post(
          "https://api.sandbox.paypal.com/v2/checkout/orders", headers=headers, json=order
      )
    print(order)

    if response.status_code == 201:
        order_data = response.json()
        return jsonify({"order_id": order_data["id"]})
    else:
        # Handle error and return appropriate response
        error_data = response.json()
        if not error_data:
            return jsonify({"error": "There has been an error"})
        return jsonify(error_data), response.status_code
