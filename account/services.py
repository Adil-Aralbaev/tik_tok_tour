from .models import Rating
from django.core.cache import cache
import random
import string
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_otp():
    return str(random.randint(100000, 999999))


def store_to_cache(identifier, value, prefix='otp', timeout=300):
    cache_key = f"{prefix}:{identifier}"
    cache.set(cache_key, value, timeout)


def get_from_cache(identifier, prefix='otp', timeout=300):
    cache_key = f"{prefix}:{identifier}"
    return cache.get(cache_key)


def verify_otp(identifier, otp_input):
    cache_key = f"otp:{identifier}"
    otp_stored = cache.get(cache_key)
    print(otp_stored)
    print(otp_input)
    if otp_stored is None:
        return False, "OTP истёк или не найден."

    if otp_stored != otp_input:
        return False, "Неверный OTP."

    cache.delete(cache_key)
    return True, "OTP успешно подтверждён."


def generate_random_password(length=10):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))


def update_user_rating(user):
    ratings = Rating.objects.filter(rated_user=user)
    count = ratings.count()
    if count == 0:
        user.rating = 0
    else:
        total = sum(r.score for r in ratings)
        user.rating = total / count
    user.save()

