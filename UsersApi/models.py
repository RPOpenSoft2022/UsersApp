from django.db import models

# Create your models here.

class User(models.Model):
	# add more relevant fields
	name = models.CharField(max_length=50)

	# change as per use
	def __str__(self):
		return self.name

class OTPModel(models.Model):
	phone_number = models.BigIntegerField()
	otp = models.CharField(max_length=6, verbose_name=" Verification Code ")
	time = models.DateTimeField(verbose_name=' Generation time ', auto_now_add=True)