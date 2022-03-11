from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MyUserSerializer
from rest_framework.views import APIView
from .models import MyUser
from rest_framework.pagination import PageNumberPagination

# This is a sample working of API
# create like this for other APIs
# GET, POST, PUT OR DELETE
@api_view(['GET'])
def testApi(request):
	return Response("Api Working!!")

@api_view(['GET'])
def getUsers(request):
	paginator = PageNumberPagination()
	if 'page_size' in request.GET:
		paginator.page_size = int(request.GET['page_size'])
	else:
		paginator.page_size = 10
	users = MyUser.objects.all()
	result_page = paginator.paginate_queryset(users, request)
	serializer = MyUserSerializer(result_page, many=True)
	return paginator.get_paginated_response(serializer.data)


@api_view(['POST'])
def createUser(request):
	serializer = MyUserSerializer(data=request.data)

	if serializer.is_valid():
		serializer.save()
	else:
		return Response({'message':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
	
	return Response(serializer.data)

@api_view(['DELETE'])
def deleteUser(request, pk):
	try:
		user = MyUser.objects.get(id=pk)
	except Exception as e:
		return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)

	user.delete()

	return Response({'message':'User data deleted'})


@api_view(['GET'])
def getSpecificUser(request, pk):
	try:
		user = MyUser.objects.get(id=pk)
	except Exception as e:
		return Response({'message':str(e)}, status=status.HTTP_400_BAD_REQUEST)

	serializer = MyUserSerializer(user)

	return Response(serializer.data)