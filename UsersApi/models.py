from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class UserManager(BaseUserManager):
	def create_user(self, phone, password=None):
		
		if not phone:
			raise ValueError("Phone Number is required")
		# if not email:
		# 	raise ValueError("Email is required")
		# if not first_name:
		# 	raise ValueError("First name is required")
		# if not last_name:
		# 	raise ValueError("Last name is required")

		user = self.model(
			phone = phone
		)

		user.set_password(password)
		user.save(using = self.db)

		return user

	def create_superuser(self, phone, password=None):
		user = self.create_user(
			password = password,
			phone = phone
		)
		user.user_category = 'Staff'
		user.is_admin = True
		user.is_superuser = True
		user.is_staff = True
		user.save(using = self.db)
		return user


class User(AbstractBaseUser):

	USER_CATEGORY = (
		('Customer', 'Customer'),
		('Staff', 'Staff'),
		('Delivery', 'Delivery')
	)

	email = models.EmailField(verbose_name="Email Address", max_length=200, null=True, blank=True)
	phone = models.BigIntegerField(verbose_name="Contact Number", unique=True, null=True)
	user_category = models.CharField(verbose_name="User Category", choices=USER_CATEGORY, default='Customer', max_length=200)
	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)

	USERNAME_FIELD = 'phone'

	REQUIRED_FIELDS = ['password']

	objects = UserManager()

	def __str__(self):
		return str(self.phone)
		
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

class Customer(models.Model):
	FOOD_PREFERENCE = (
		('Veg', 'Veg'),
		('Non Veg', 'Non Veg'),
		('Normal', 'Normal')
	)

	first_name = models.CharField(verbose_name="First Name", max_length=200)
	middle_name = models.CharField(verbose_name="Middle Name", max_length=200, null=True, blank=True)
	last_name = models.CharField(verbose_name="Last Name", max_length=200, null=True, blank=True)
	address = models.TextField(verbose_name="Address", null=True, blank=True)
	age = models.IntegerField(verbose_name="Age", null=True, blank=True)
	gender = models.CharField(verbose_name="Gender", max_length=200, null=True, blank=True)
	food_preference = models.CharField(verbose_name="Food Preference", choices = FOOD_PREFERENCE, max_length = 200, default='Normal')
	user = models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.first_name + ' ' + (self.last_name if self.last_name else '') 

	
	
