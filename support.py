from flask import Blueprint, request, jsonify
from models import db, Order, User
import openai
import os

support_bp = Blueprint('support', __name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")


@support_bp.route("/api/support/resolve", methods=["POST"])
def auto_resolve_ticket():
    order_id = request.json.get("order_id")
    complaint = request.json.get("complaint")

    order = Order.query.filter_by(id=order_id).first()
    user = User.query.filter_by(id=order.user_id).first()

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Customer complaint: {complaint}\nOrder total: {order.total}\nShould we issue a refund? Reply with REFUND or NO_REFUND and reason."
            }
        ]
    )

    decision = response.choices[0].message.content

    if "REFUND" in decision:
        order.status = "refunded"
        user.credits += order.total
        db.session.commit()

    return jsonify({"decision": decision, "order_id": order_id})


@support_bp.route("/api/support/escalate", methods=["POST"])
def escalate_ticket():
    ticket_id = request.json.get("ticket_id")
    conversation = request.json.get("conversation")

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Based on this support conversation, should this be escalated to a manager? {conversation}\nReply with ESCALATE or RESOLVE."
            }
        ]
    )

    decision = response.choices[0].message.content

    if "ESCALATE" in decision:
        notify_manager(ticket_id)
    else:
        close_ticket(ticket_id)

    return jsonify({"decision": decision})


def notify_manager(ticket_id):
    pass


def close_ticket(ticket_id):
    pass
