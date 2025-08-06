from django.db import models
from django.conf import settings

from account.models import User


class Tour(models.Model):
    image = models.ImageField(upload_to='tour_images/')
    title = models.CharField(max_length=50)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='tours')
    active = models.BooleanField(default=True)
    description = models.TextField()
    price = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    place = models.CharField(max_length=50) # место назначения

    class Level(models.TextChoices):
        HARD = 'Hard'
        MEDIUM = 'Medium'
        EASY = 'Easy'

    level = models.CharField(max_length=6,
                             choices=Level.choices,
                             default=Level.EASY)

    rating = models.FloatField(default=5)
    rating_counts = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        author = User.objects.get(id=self.author.id)
        if author.role != 'AR':
            raise ValueError('Only authors can create a tours')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class TourDate(models.Model):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name='dates')
    date = models.DateTimeField()
    available_slots = models.PositiveIntegerField()
    duration_days = models.IntegerField(default=1)  # длительность тура
    collection_point = models.CharField(max_length=50)  # точка сбора

    class Meta:
        unique_together = ('tour', 'date')


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user'
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='tour'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tour')


class Rating(models.Model):
    # Кто оставил рейтинг
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rater'
    )

    tour = models.ForeignKey(
        Tour, related_name='ratings',
        on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rater', 'tour')

    def __str__(self):
        return f'{self.rater} → {self.tour}: {self.score}'

