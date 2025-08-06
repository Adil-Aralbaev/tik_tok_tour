from datetime import date
from rest_framework import serializers
from django.db import IntegrityError

from .models import Rating, Tour, Favorite, TourDate


class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['image', 'title', 'author', 'active',
                  'description', 'price', 'created',
                  'updated', 'place', 'level', 'rating']
        read_only_fields = ['rating', 'author', 'created', 'updated']


class TourDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourDate
        fields = '__all__'

    def validate_date(self, value):
        if value.date() < date.today():
            raise serializers.ValidationError("Дата тура не может быть в прошлом.")
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'tour', 'created_at', 'user']
        read_only_fields = ['created_at', 'user']


class FavoriteDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite


class TourRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['rater', 'created_at']



