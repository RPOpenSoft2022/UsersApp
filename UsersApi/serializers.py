from rest_framework import serializers
from .models import User

# add serializers
# change as per use
class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields ='__all__'