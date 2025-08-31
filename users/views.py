import uuid

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache
from django.contrib.auth.hashers import make_password

from .models import User
from .serializers import UserRegistrationSerializer, ForgotPasswordSerializer, ResetPasswordSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    throttle_classes = [AnonRateThrottle]
    pass


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4())
            cache.set(f'reset_{token}', user.id, timeout=600)  # 10 min expiry
            return Response({"message": "Reset token generated", "token": token})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class ResetPasswordView(APIView):
    throttle_classes = [AnonRateThrottle]
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        user_id = cache.get(f'reset_{token}')
        if user_id:
            user = User.objects.get(id=user_id)
            user.password = make_password(serializer.validated_data['new_password'])
            user.save()
            cache.delete(f'reset_{token}')
            return Response({"message": "Password reset successfully"})
        return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)