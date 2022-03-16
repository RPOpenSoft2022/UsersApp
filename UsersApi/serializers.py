from rest_framework import serializers
from .models import *

# add serializers
# change as per use
class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		# fields ='__all__'
		exclude = ('last_login', 'is_admin', 'is_staff', 'is_superuser', 'is_active', 'password')

class CustomerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Customer
		fields ='__all__'
