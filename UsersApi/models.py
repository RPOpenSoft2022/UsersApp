from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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
			email = self.normalize_email(email),
			first_name = first_name,
			last_name = last_name,
			phone = phone
		)

		user.set_password(password)
		user.save(using = self.db)

		return user

	def create_superuser(self, email, phone, first_name, last_name, password=None):
		user = self.create_user(
			email = self.normalize_email(email),
			first_name = first_name,
			last_name = last_name,
			password = password,
			phone = phone
		)

		user.is_admin = True
		user.is_superuser = True
		user.is_staff = True
		user.save(using = self.db)
		return user


class MyUser(AbstractBaseUser):

	USER_CATEGORY = (
		('Customer', 'Customer'),
		('Staff', 'Staff'),
		('Delivery', 'Delivery')
	)

	email = models.EmailField(verbose_name="Email Address", max_length=200, unique=True)
	first_name = models.CharField(verbose_name="First Name", max_length=200, null=True, blank=True)
	middle_name = models.CharField(verbose_name="Middle Name", max_length=200, null=True, blank=True)
	last_name = models.CharField(verbose_name="Last Name", max_length=200, null=True, blank=True)
	phone = models.BigIntegerField(verbose_name="Contact Number", null=True, blank=True, unique=True)
	address = models.TextField(null=True, blank=True)
	age = models.IntegerField(verbose_name="Age", null=True, blank=True)
	gender = models.CharField(verbose_name="Gender", max_length=200, null=True, blank=True)
	user_category = models.CharField(verbose_name="User Category", choices=USER_CATEGORY, default='Customer', max_length=200)
	current_location = models.DecimalField(verbose_name="Current Location",max_digits=22,
    decimal_places=16, null=True, blank=True)
	last_updated_location = models.DecimalField(verbose_name="Last Updated Location",max_digits=22,
    decimal_places=16, null=True, blank=True)

	is_admin = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)

	USERNAME_FIELD = "email"

	REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'phone']

	objects = MyUserManager()

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return True
	
	def has_module_perms(self, app_label):
		return True

# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client
import random

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
#account_sid = os.environ['ACf55b59ed14d54f24075833dedd87fcc9']
#auth_token = os.environ['7bb0fcad734cdf5d2fe253f303d4a3b9']
#client = Client(account_sid, auth_token)
#
#message = client.messages \
#                .create(
#                     body="send otp",
#                     from_='+19712487862',
#                     to='+917070666966'
#                 )
#
#print(message.sid)
#
#otp=random.randint(1000,9999)
#print(otp)
#
#account_sid = 'ACf55b59ed14d54f24075833dedd87fcc9'
#auth_token = '7bb0fcad734cdf5d2fe253f303d4a3b9'
#client = Client(account_sid,auth_token)
#
#message = client.messages.create(
#	body = 'Your OTP is '+str(otp),
#	from_='+19712487862',
#     to='+917070666966'
#)
#print (message.sid)
class OTP(models.Model):
	def save(self,*args,**kwargs):
		account_sid = 'ACf55b59ed14d54f24075833dedd87fcc9'
		auth_token = '7bb0fcad734cdf5d2fe253f303d4a3b9'
		client = Client(account_sid,auth_token)
		otp=random.randint(1000,9999)
		print(otp)
		message = client.messages.create(
 			body = 'Your OTP is '+str(otp),
			from_='+19712487862',
     		to='+917070666966')
		print(message.id)    
		return super().save(*args, **kwargs)
