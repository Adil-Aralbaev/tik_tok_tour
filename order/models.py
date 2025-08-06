from django.db import models

from account.models import User
from tour.models import TourDate


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='orders')
    tour_date = models.ForeignKey(TourDate,
                                  on_delete=models.CASCADE,
                                  related_name='orders')
    quantity = models.IntegerField(default=1)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    def get_total_price(self):
        return self.tour_date.tour.price * self.quantity



