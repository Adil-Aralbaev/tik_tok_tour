from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'tour_date', 'quantity', 'paid', 'created', 'total_price']
        read_only_fields = ['id', 'total_price', 'paid', 'created', 'user']

    def get_total_price(self, obj):
        return obj.get_total_price()
