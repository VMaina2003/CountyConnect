from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from cloudinary.models import CloudinaryField

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.role = CustomUser.UserRole.VIEWER
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', CustomUser.UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class UserRole(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        County_Official= 'EDITOR', 'Editor'
        Citizen = 'WRITER', 'Writer'
        VIEWER = 'VIEWER', 'Viewer'
        
        
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.VIEWER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username if self.username else self.email

    # Role check methods
    def is_admin(self):
        return self.role == self.UserRole.ADMIN
    
    def is_official(self):
        return self.role == self.UserRole.County_Official
    
    def is_citizen(self):
        return self.role == self.UserRole.Citizen
    
    def is_viewer(self):
        return self.role == self.UserRole.VIEWER
    
    def get_display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username if self.username else self.email

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=30, blank=True)
    avatar = CloudinaryField('image', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile" if self.user.username else f"{self.user.email}'s profile"  