from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MyUserSerializer
from rest_framework.views import APIView
from .models import MyUser
from datetime import date, datetime
import jwt
from django.contrib.auth.models import auth
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
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data)


@api_view(['DELETE'])
def deleteUser(request, pk):
    try:
        user = MyUser.objects.get(id=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()

    return Response({'message': 'User data deleted'})


@api_view(['GET'])
def getSpecificUser(request, pk):
    try:
        user = MyUser.objects.get(id=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MyUserSerializer(user)

    return Response(serializer.data)


@api_view(['POST'])
def login(request):
    phone = request.data.get('phone')
    user = MyUser.objects.get(phone=phone)
    if user is not None: 
        user = auth.authenticate(phone=request.data['password'], password= request.data['phone'])
        if user is not None:
            payload = {
                'id': user.phone,
                'exp': datetime.utcnow() + datetime.timedelta(minutes=5),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')

            response = Response()
            serializer = MyUserSerializer(user)
            response.data = {
                'token': token,
                'user': serializer.data,
                'message': 'Logged in succesfully',
            }
            return response
        else:
            content = {'message': 'incorrect password2'}
    else:
        content = {'message': 'incorrect password1'}

    return Response(content, status=status.HTTP_400_BAD_REQUEST)
