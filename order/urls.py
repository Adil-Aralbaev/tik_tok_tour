from django.urls import path, include
from .views import OrderListView, OrderDetailView

urlpatterns = [
    path('', OrderListView.as_view()),             # GET (list), POST
    path('<int:pk>/', OrderDetailView.as_view()),    # PUT, DELETE
]

