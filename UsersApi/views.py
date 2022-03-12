from os import stat
from pstats import Stats
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tokens import get_tokens_for_user
from .models import OTPModel
from .serializers import MyUserSerializer
from rest_framework.views import APIView
from .models import MyUser, MyUserManager
from datetime import date, datetime
import jwt
from django.contrib.auth.models import auth
from rest_framework.pagination import PageNumberPagination
from datetime import timedelta
from django.utils import timezone
from .utilities import validate_token
from twilio.rest import Client
import random


@api_view(['GET'])
def getUsers(request):
    token = request.data.get('token')
    enc_info = validate_token(token)
    if not enc_info:
        return Response(data={"message":"Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)
    
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
    token = request.data.get('token')

    serializer = MyUserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
    else:
        return Response({'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(data={"message": "user created, now you can login."})


@api_view(['DELETE'])
def deleteUser(request, pk):    
    token = request.data.get('token')
    enc_info = validate_token(token)
    if not enc_info:
        return Response(data={"message":"Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        user = MyUser.objects.get(id=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()

    return Response({'message': 'User data deleted'})


@api_view(['GET'])
def getSpecificUser(request, pk):
    token = request.data.get('token')
    enc_info = validate_token(token)
    if not enc_info:
        return Response(data={"message":"Invalid Token"}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        user = MyUser.objects.get(id=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MyUserSerializer(user)

    return Response(serializer.data)


@api_view(['POST'])
def login(request):
    phone = request.data.get('phone')
    try:
        user = MyUser.objects.get(phone=phone)
        password = request.data.get('password')
        if user.check_password(password):
            payload = {
                'phone': user.phone,
                'exp': datetime.utcnow() + timedelta(seconds=5*60),
                'iat': datetime.utcnow()
            }
            token = jwt.encode(payload, 'secret', algorithm='HS256')
            response = Response()
            response.data = {
                'token': token,
                'message': 'Logged in succesfully',
            }
            return response
        else:
            content = {'message': 'incorrect password'}
    except:
        content = {'message': 'incorrect phone number'}

    return Response(content, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def sendOTP(request):
    phone = request.data['phone']
	
    try:
        otp_row = OTPModel.objects.get(phone=phone)
    except:
        otp_row = None

    if otp_row:
        if otp_row.valid_until > timezone.now():
            return Response(data={"message": "OTP already sent"})
        otp_row.delete()
    account_sid='ACf55b59ed14d54f24075833dedd87fcc9'
    auth_token = '7bb0fcad734cdf5d2fe253f303d4a3b9'
    client = Client(account_sid,auth_token)
    otp=random.randint(1000,9999)
    print(otp)
    message = client.messages.create(
        body = 'Your OTP is '+str(otp),
        from_='+19712487862',
        to='+917070666966')
    newOTP = OTPModel(phone=phone, otp=999999)
    newOTP.save()
    return Response(data={"message": "OTP send"})


@api_view(['POST'])
def verifyOTP(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')

    if phone and otp:
        try:
            otp_row = OTPModel.objects.get(phone=phone)
        except:
            otp_row = None

        if otp_row:
            if otp_row.otp == otp and otp_row.valid_until > timezone.now(): 
                otp_row.delete()  
                payload = {
                    'phone': phone,
                    'exp': datetime.utcnow() + timedelta(seconds=5*60),
                    'iat': datetime.utcnow()
                }
                token = jwt.encode(payload, 'secret', algorithm='HS256')

                return Response(data={"token": token})

            return Response(data={"message": "OTP invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        
    return Response(status=status.HTTP_400_BAD_REQUEST)
