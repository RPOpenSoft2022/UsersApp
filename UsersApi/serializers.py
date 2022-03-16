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
<<<<<<< HEAD
		fields ='__all__'
=======
		fields ='__all__'
>>>>>>> a113455dc421ba8539b68e5bb3b375a3f71f629a
