from django.urls import path

from .views import CreateStripeSessionAPIView

urlpatterns = [
    path('<int:order_id>/pay/', CreateStripeSessionAPIView.as_view()),
]
