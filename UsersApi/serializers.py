from rest_framework import serializers
from .models import MyUser

# add serializers
# change as per use
class MyUserSerializer(serializers.ModelSerializer):
	class Meta:
		model = MyUser
		# fields ='__all__'
		exclude = ('last_login', 'is_admin', 'is_staff', 'is_superuser', 'is_active', 'password')