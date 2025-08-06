from django.urls import path

from .views import RatingView, UserListCreateAPIView, \
                   UserDetailAPIView, LogoutView, \
                   ResetPasswordView, ForgotPasswordView, \
                   Profile, RegisterWithEmailView, \
                   TelegramLoginStartView, LoginWithEmailView, VerifyOTPView


urlpatterns = [
    path('', UserListCreateAPIView.as_view()),
    path('<int:pk>/', UserDetailAPIView.as_view()),
    path('user-rating/', RatingView.as_view()),
    path('profile/', Profile.as_view()),

    path('register-with-email/', RegisterWithEmailView.as_view()),
    path('auth-with-tg/', TelegramLoginStartView.as_view()),
    path('auth-with-email/', LoginWithEmailView.as_view()),
    path('otp-verify/', VerifyOTPView.as_view()),

    path('logout/', LogoutView.as_view(), name='logout'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
]
