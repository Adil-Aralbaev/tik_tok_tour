import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse

from order.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(csrf_exempt, name='dispatch')
class CreateStripeSessionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            if order.paid:
                return Response({"detail": "Order already paid."}, status=400)

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'kgs',  # Stripe не поддерживает KGS напрямую
                        'unit_amount': int(order.get_total_price() * 100),  # цена в центах
                        'product_data': {
                            'name': f'Tour on {order.tour_date.date}',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.DOMAIN}/success/",
                cancel_url=f"{settings.DOMAIN}/cancel/",
                metadata={"order_id": order.id},
            )

            order.stripe_session_id = session.id
            order.save()

            return Response({'checkout_url': session.url})
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Обработка события
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.save()
            except Order.DoesNotExist:
                pass

    return HttpResponse(status=200)

