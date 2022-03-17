from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class UserManager(BaseUserManager):
	def create_user(self, phone, email, password=None):
		
		if not phone:
			raise ValueError("Phone Number is required")
		if not email:
			raise ValueError("Email is required")
		# if not first_name:
		# 	raise ValueError("First name is required")
		# if not last_name:
		# 	raise ValueError("Last name is required")

		user = self.model(
			email = self.normalize_email(email),
			phone = phone
		)

		user.set_password(password)
		user.save(using = self.db)

		return user

	def create_superuser(self, email, phone, password=None):
		user = self.create_user(
			email = self.normalize_email(email),
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

	email = models.EmailField(verbose_name="Email Address", max_length=200)
	# name = models.CharField(verbose_name="Name", max_length=200, blank=True)
	# first_name = models.CharField(verbose_name="First Name", max_length=200, null=True, blank=True)
	# middle_name = models.CharField(verbose_name="Middle Name", max_length=200, null=True, blank=True)
	# last_name = models.CharField(verbose_name="Last Name", max_length=200, null=True, blank=True)
	phone = models.BigIntegerField(verbose_name="Contact Number", unique=True, null=True)
	# address = models.TextField(null=True, blank=True)
	# age = models.IntegerField(verbose_name="Age", null=True, blank=True)
	# gender = models.CharField(verbose_name="Gender", max_length=200, null=True, blank=True)
	user_category = models.CharField(verbose_name="User Category", choices=USER_CATEGORY, default='Customer', max_length=200)

	# delivery partner specific fields
	# current_lat = models.DecimalField(verbose_name="Current Latitude",max_digits=22,
    # decimal_places=16, null=True, blank=True)
	# current_long = models.DecimalField(verbose_name="Current Longitude",max_digits=22,
    # decimal_places=16, null=True, blank=True)
	# last_updated_location_time = models.DateTimeField(verbose_name="Last updated location time", null=True, blank=True)
	# is_free = models.BooleanField(default=True)

	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)

	USERNAME_FIELD = 'phone'

	REQUIRED_FIELDS = ['email', 'password']

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
	)

	first_name = models.CharField(verbose_name="First Name", max_length=200, null=True, blank=True)
	middle_name = models.CharField(verbose_name="Middle Name", max_length=200, null=True, blank=True)
	last_name = models.CharField(verbose_name="Last Name", max_length=200, null=True, blank=True)
	address = models.TextField(verbose_name="Address", null=True, blank=True)
	age = models.IntegerField(verbose_name="Age", null=True, blank=True)
	gender = models.CharField(verbose_name="Gender", max_length=200, null=True, blank=True)
	food_preference = models.CharField(verbose_name="Food Preference", choices = FOOD_PREFERENCE, max_length = 200, default='Normal')
	user = models.OneToOneField(User, verbose_name="User", on_delete=models.CASCADE, null=True, blank=True)

	def __str__(self):
		return self.first_name + ' ' + self.last_name 

	
	
