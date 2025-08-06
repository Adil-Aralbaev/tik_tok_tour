from django.contrib import admin

from .models import Rating, Tour, TourDate, Favorite

admin.site.register(Rating)
admin.site.register(Tour)
admin.site.register(TourDate)
admin.site.register(Favorite)