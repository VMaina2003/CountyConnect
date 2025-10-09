from django.urls import path
from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    ProfileView,
    RequestPasswordResetView,
    PasswordResetConfirmView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
]
