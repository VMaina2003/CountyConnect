from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from .models import Profile

User = get_user_model()


#  Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        Profile.objects.create(user=user)  
        return user


#  Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials or user does not exist.")
        if not user.is_active:
            raise serializers.ValidationError("Account is inactive. Please verify your email.")

        return user


#  User Serializer 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username',
            'first_name', 'last_name',
            'role', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'date_joined']


#  Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['user', 'bio', 'phone', 'location', 'avatar']

    def update(self, instance, validated_data):
        # Allow updating nested user fields if provided
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.user.save()
        instance.save()
        return instance


# Password Reset Request Serializer
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


#  Set New Password Serializer
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"}
    )

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    def save(self, **kwargs):
        password = self.validated_data['password']
        user = self.context.get('user')
        user.set_password(password)
        user.save()
        return user
    