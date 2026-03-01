from flask import Blueprint, request, jsonify, render_template_string
import openai
import os

formatter_bp = Blueprint('formatter', __name__)

openai.api_key = os.environ.get("OPENAI_API_KEY")


@formatter_bp.route("/api/format/response", methods=["POST"])
def format_response():
    user_message = request.json.get("message")
    response_type = request.json.get("type", "html")

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Format this customer support response as {response_type}: {user_message}"
            }
        ]
    )

    llm_output = response.choices[0].message.content

    if response_type == "html":
        rendered = render_template_string(f"<div class='support-response'>{llm_output}</div>")
        return rendered

    return jsonify({"formatted": llm_output})


@formatter_bp.route("/api/format/receipt", methods=["POST"])
def format_receipt():
    order_data = request.json.get("order_data")

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Generate an HTML receipt for this order: {order_data}"
            }
        ]
    )

    receipt_html = response.choices[0].message.content

    return f"""
    <html>
        <body>
            <div class='receipt'>
                {receipt_html}
            </div>
        </body>
    </html>
    """


@formatter_bp.route("/api/format/email", methods=["POST"])
def format_email():
    customer_name = request.json.get("customer_name")
    issue = request.json.get("issue")

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": f"Write a support email for {customer_name} regarding: {issue}"
            }
        ]
    )

    email_content = response.choices[0].message.content

    template = f"""
    <html>
        <body>
            {email_content}
        </body>
    </html>
    """

    return render_template_string(template)
