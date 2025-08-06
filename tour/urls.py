from django.urls import path, include

from rest_framework import routers
from .views import RatingView, FavoriteView, \
                   TourDateListCreateView, TourDateDetailView, \
                   FavoriteDetailView, \
                   TourListCreateAPIView, TourDetailAPIView, \
                   TourDateForTourListCreateView, TourDateForTourDetailView

urlpatterns = [
    path('', TourListCreateAPIView.as_view()),
    path('<int:pk>/', TourDetailAPIView.as_view()),

    path('rating/', RatingView.as_view()),

    path('favorite/', FavoriteView.as_view()),
    path('favorite/<int:pk>/', FavoriteDetailView.as_view()),

    path('tour-dates/', TourDateListCreateView.as_view()),
    path('tour-dates/<int:pk>/', TourDateDetailView.as_view()),
    path('<int:tour_id>/tour-dates/', TourDateForTourListCreateView.as_view()),
    path('<int:tour_id>/tour-dates/<int:date_id>/', TourDateForTourDetailView.as_view())
]
