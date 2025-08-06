from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings

from .models import User, Rating
from .services import generate_otp, store_to_cache


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ['id', 'image', 'login', 'is_verified', 'birth_date',
                  'role', 'phone_number', 'level', 'description',
                  'rating', 'first_name', 'last_name']
        read_only_fields = ['rating', 'role']


class RatingSerializer(serializers.ModelSerializer):
    rated_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Rating
        fields = ['rater', 'rated_user', 'score', 'created_at']
        read_only_fields = ['rater', 'created_at']


# register and authentication
class RegisterWithEmailSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_login(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        username = validated_data['login']
        email = validated_data['email']
        password = validated_data['password']

        user = User(username=username, login=username, email=email)
        user.set_password(password)
        user.is_active = True
        user.is_verified = False

        otp_code = generate_otp()
        store_to_cache(user.email, otp_code, timeout=180)

        send_mail(
            subject='🔐 Ваш одноразовый код (OTP)',
            message=(
                f'Здравствуйте, {username}!\n\n'
                f'Ваш одноразовый код (OTP): {otp_code}\n\n'
                f'Пожалуйста, введите этот код для завершения входа или подтверждения действия.\n'
                f'Срок действия кода — несколько минут.\n\n'
                f'Не сообщайте этот код другим людям — это необходимо для вашей безопасности.\n\n'
                f'С уважением,\nКоманда поддержки'
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        user.save()
        return user


class LoginWithEmailSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True)


class TelegramLoginStartSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()


class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['image', 'login', 'is_verified', 'birth_date', 'role',
                  'phone_number', 'level', 'description', 'rating', 'username']
        read_only_fields = ['is_verified', 'role', 'level', 'rating']
