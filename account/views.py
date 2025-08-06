from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from .models import User, Rating
from .serializers import UserSerializer, RatingSerializer, \
                         RegisterWithEmailSerializer, LoginWithEmailSerializer, \
                         TelegramLoginStartSerializer, OTPVerifySerializer, ProfileSerializer
from account.permissions import IsAdminOrReadOnly
from .services import get_tokens_for_user, verify_otp

BOT_USERNAME = 'test_bot_for_tour_bot'


class UserListCreateAPIView(ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return User.objects.all()

    def perform_create(self, serializer):
        return serializer.save()


class UserDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return User.objects.all()


class RatingView(GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.all()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rater = request.user
        rated_user = serializer.validated_data['rated_user']
        score = serializer.validated_data['score']

        if rater == rated_user:
            raise serializers.ValidationError('Нельзя ставить рейтинг самому себе.')

        rating, created = Rating.objects.update_or_create(
            rater=rater,
            rated_user=rated_user,
            defaults={'score': score}
        )

        total_score = rated_user.rating * rated_user.rating_counts
        rated_user.rating_counts += 1
        rated_user.rating = round((total_score + score) / rated_user.rating_counts, 2)
        rated_user.save()

        return Response(self.get_serializer(rating).data, status=201)


# registration and authantication

class RegisterWithEmailView(GenericAPIView):
    serializer_class = RegisterWithEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_201_CREATED)


class LoginWithEmailView(GenericAPIView):
    serializer_class = LoginWithEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not user.check_password(password):
            return Response({"detail": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)


class VerifyOTPView(GenericAPIView):
    serializer_class = OTPVerifySerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.user.email
        return Response({"email": email})

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        otp_input = serializer.validated_data['otp']
        email = request.user.email

        if email:
            is_valid, message = verify_otp(email, otp_input)
        else:
            return Response({"error": "Email address is missing or invalid."})

        if not is_valid:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
        request.user.is_verified = True
        request.user.save()
        return Response({"detail": message}, status=status.HTTP_200_OK)


class TelegramLoginStartView(GenericAPIView):
    serializer_class = TelegramLoginStartSerializer

    def get(self, request):
        return Response({
            "chat_url": f"https://t.me/{BOT_USERNAME}?start=start",
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        print(phone_number)
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response('Введенный номер не корректен')
        print(otp)
        is_valid, message = verify_otp(identifier=user.chat_id, otp_input=otp)
        if is_valid:
            user.is_verified = True
            print(message)
        else:
            return Response(message)

        refresh = RefreshToken.for_user(user)

        refresh.payload.update({
            'user_id': user.id,
            'username': user.username
        })

        print(refresh)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)


class Profile(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def get(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Вы успешно вышли из системы."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Ошибка при выходе из системы."}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(GenericAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"http://your-frontend.com/reset-password/{uid}/{token}/"

        send_mail(
            subject='Сброс пароля',
            message=f'Ссылка для сброса пароля: {reset_url}',
            from_email='noreply@example.com',
            recipient_list=[email],
        )

        return Response({'detail': 'Письмо со ссылкой на сброс пароля отправлено.'})


class ResetPasswordView(GenericAPIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'error': 'Неверная ссылка'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Неверный или устаревший токен.'}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        if not password:
            return Response({'error': 'Пароль обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        user.save()

        return Response({'detail': 'Пароль успешно обновлён.'}, status=status.HTTP_200_OK)