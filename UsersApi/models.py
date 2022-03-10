from django.db import models

# Create your models here.

class User(models.Model):
	# add more relevant fields
	name = models.CharField(max_length=50)

	# change as per use
	def __str__(self):
		return self.name