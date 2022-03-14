from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta

# Create your models here.


class MyUserManager(BaseUserManager):
    def create_user(self, phone, email, first_name, last_name, password=None):

        if not phone:
            raise ValueError("Phone Number is required")
        if not email:
            raise ValueError("Email is required")
        if not first_name:
            raise ValueError("First name is required")
        if not last_name:
            raise ValueError("Last name is required")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )

        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, phone, first_name, last_name, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            password=password,
            phone=phone
        )
        user.user_category = 'Staff'
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self.db)
        return user


class MyUser(AbstractBaseUser):

    email = models.EmailField(
        verbose_name="Email Address", max_length=200, unique=True)
    name = models.CharField(verbose_name="Name", max_length=200, blank=True)
    first_name = models.CharField(
        verbose_name="First Name", max_length=200, null=True, blank=True)
    middle_name = models.CharField(
        verbose_name="Middle Name", max_length=200, null=True, blank=True)
    last_name = models.CharField(
        verbose_name="Last Name", max_length=200, null=True, blank=True)
    phone = models.BigIntegerField(
        verbose_name="Contact Number", unique=True, null=False)
    address = models.TextField(verbose_name="Contact Address", null=True, blank=True)
    age = models.IntegerField(verbose_name="Age", null=True, blank=True)
    gender = models.CharField(verbose_name="Gender",
                              max_length=200, null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'password']

    objects = MyUserManager()

    def __str__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class OTPModel(models.Model):
    phone = models.BigIntegerField()
    otp = models.CharField(max_length=6, verbose_name=" Verification Code ")
    valid_until = models.DateTimeField(
        default=timezone.now() + timedelta(seconds=300),
        help_text="The timestamp of the moment of expiry of the saved token."
    )
