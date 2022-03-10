from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer

from .models import User

# This is a sample working of API
# create like this for other APIs
# GET, POST, PUT OR DELETE
@api_view(['GET'])
def testApi(request):
	return Response("Api Working!!")