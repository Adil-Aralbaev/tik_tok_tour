from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    login = models.CharField(max_length=150, unique=True)
    is_verified = models.BooleanField(default=False)
    birth_date = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=150)

    class Role(models.TextChoices):
        AUTHOR = 'AR', 'Author'
        USER = 'UR', 'User'
        GUIDE = 'GD', 'Guide'

    role = models.CharField(max_length=2,
                            choices=Role.choices,
                            default=Role.USER)

    phone_number = models.CharField(unique=True, max_length=13, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['phone_number'],
                condition=~models.Q(phone_number=None),
                name='unique_phone_number_not_null'
            )
        ]

    chat_id = models.CharField(max_length=15, null=True, blank=True)

    class Level(models.TextChoices):
        BRONZE = 'BR', 'Bronze'
        SILVER = 'SL', 'Silver'
        GOLD = 'GL', 'Gold'

    level = models.CharField(max_length=2,
                             choices=Level.choices,
                             default=Level.BRONZE)

    description = models.TextField(null=True, blank=True)

    rating = models.FloatField(default=5)
    rating_counts = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Rating(models.Model):
    # Кто оставил рейтинг
    rater = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_ratings'
    )

    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='received_ratings',
        on_delete=models.CASCADE
    )
    score = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('rater', 'rated_user')

    def __str__(self):
        return f'{self.rater} → {self.rated_user}: {self.score}'


