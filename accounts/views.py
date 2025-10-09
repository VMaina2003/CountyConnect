from rest_framework import status, generics, permissions
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile
from .utils import send_email
from .tokens import email_verification_token
from .serializers import (
    RegisterSerializer,
    ResetPasswordSerializer,
    SetNewPasswordSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileSerializer
)
from .permissions import IsCitizenOrCountyOfficialOrAdmin
from rest_framework import exceptions
from django.contrib.auth import get_user_model

User = get_user_model()



#  Register User + Email Verify

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny] 

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        token = email_verification_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verify_link = f"http://127.0.0.1:8000/api/accounts/verify-email/{uid}/{token}/"
        send_email(
            subject="Verify your CountyConnect account",
            message=f"Hi {user.first_name or user.email},\nClick the link to verify your email: {verify_link}",
            recipient=user.email
        )



#  Verify Email

class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]  

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and email_verification_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({'message': 'Email verified successfully!'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid or expired verification link.'}, status=status.HTTP_400_BAD_REQUEST)


#  Login (JWT)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]  

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsCitizenOrCountyOfficialOrAdmin]

    def get_object(self):
        """
        Get or create the authenticated user's profile.
        """
        if self.request.user.is_anonymous:
            raise exceptions.NotAuthenticated("Authentication credentials were not provided.")
        
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def update(self, request, *args, **kwargs):
        """
        Support partial updates (PATCH) and full updates (PUT).
        """
        partial = kwargs.pop('partial', True)  
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)




#  Request Password Reset

class RequestPasswordResetView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]  

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"http://127.0.0.1:8000/api/accounts/reset-password/{uid}/{token}/"
            send_email(
                subject="Reset your CountyConnect password",
                message=f"Hi,\nClick the link below to reset your password:\n{reset_link}",
                recipient=user.email
            )

        return Response({'message': 'If this email exists, a reset link was sent.'}, status=status.HTTP_200_OK)



#  Confirm Password Reset

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    permission_classes = [permissions.AllowAny] 

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Invalid link.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'message': 'Password reset successful!'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
