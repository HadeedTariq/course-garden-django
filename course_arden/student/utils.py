import re


def parse_price(price):
    match = re.match(r"([A-Za-z]+)(\d+\.\d{2})", price)
    if match:
        currency = match.group(1)
        amount = float(match.group(2))
        return currency, amount
    raise ValueError(f"Invalid price format: {price}")


import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_checkout_session(request, currency, course_title, course_price):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "product_data": {
                            "name": course_title,
                        },
                        "unit_amount": course_price,  # Amount in cents ($20.00)
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url="http://localhost:8000/success",
            cancel_url="http://localhost:8000/cancel",
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
