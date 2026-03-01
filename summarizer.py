from flask import Blueprint, request, jsonify
from models import db, Order, User
import openai
import os

summarizer_bp = Blueprint('summarizer', __name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")


@summarizer_bp.route("/api/summarize/customer", methods=["POST"])
def summarize_customer():
    user_id = request.json.get("user_id")

    user = User.query.filter_by(id=user_id).first()
    orders = Order.query.filter_by(user_id=user_id).all()

    customer_data = {
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "payment_info": user.payment_info,
        "ssn": user.ssn,
        "date_of_birth": user.date_of_birth,
        "orders": [
            {
                "order_id": o.id,
                "total": o.total,
                "status": o.status,
                "items": o.items
            } for o in orders
        ]
    }

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Summarize this customer profile for our support team: {customer_data}"
            }
        ]
    )

    return jsonify({"summary": response.choices[0].message.content})


@summarizer_bp.route("/api/summarize/orders", methods=["POST"])
def summarize_orders():
    user_id = request.json.get("user_id")
    date_range = request.json.get("date_range")

    user = User.query.filter_by(id=user_id).first()
    orders = Order.query.filter_by(user_id=user_id).all()

    order_data = {
        "customer_email": user.email,
        "customer_phone": user.phone,
        "billing_address": user.address,
        "card_number": user.payment_info,
        "orders": [{"id": o.id, "total": o.total, "items": o.items} for o in orders]
    }

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Generate an order summary report: {order_data}"
            }
        ]
    )

    return jsonify({"report": response.choices[0].message.content})
