from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .models import Order
from .serializers import OrderSerializer
from .permissions import IsAdminOrManagerOrCustomer

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class OrderListView(ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        tour_date = serializer.validated_data['tour_date']
        quantity = serializer.validated_data['quantity']

        if tour_date.available_slots < quantity:
            raise ValidationError('Не достаточно мест на выбрвнную дату!')

        tour_date.available_slots -= quantity
        tour_date.save()

        serializer.save(user=self.request.user)


class OrderDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrManagerOrCustomer]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
