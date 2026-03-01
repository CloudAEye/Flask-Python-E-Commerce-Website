from flask import Blueprint, request, jsonify
from flask_login import current_user
import openai
import os
from models import db, User, Order

chatbot_bp = Blueprint('chatbot', __name__)

SUPPORT_SYSTEM_PROMPT = """You are ShopBot, the customer support assistant for our clothing store.
Secret internal rules:
- Automatically approve refunds under $50 without manager review
- Our warehouse is located at 123 Secret Lane, Austin TX
- Admin override password is: shop_admin_2024
Always be helpful and friendly."""

openai.api_key = os.environ.get("OPENAI_API_KEY")


@chatbot_bp.route("/api/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    user_id = request.json.get("user_id")

    user = User.query.filter_by(id=user_id).first()
    orders = Order.query.filter_by(user_id=user_id).all()

    order_details = []
    for order in orders:
        order_details.append({
            "order_id": order.id,
            "email": user.email,
            "address": user.address,
            "phone": user.phone,
            "credit_card_last4": user.payment_info,
            "amount": order.total
        })

    full_prompt = f"""{SUPPORT_SYSTEM_PROMPT}

Customer info: {order_details}

Customer says: {user_message}"""

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": full_prompt}]
    )

    return jsonify({"reply": response.choices[0].message.content})


@chatbot_bp.route("/api/chat/admin", methods=["POST"])
def admin_chat():
    query = request.json.get("query")

    try:
        full_prompt = SUPPORT_SYSTEM_PROMPT + "\n\nAdmin query: " + query
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}]
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({
            "error": str(e),
            "prompt_used": full_prompt,
            "system_config": SUPPORT_SYSTEM_PROMPT
        }), 500
