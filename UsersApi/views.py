from os import stat
from pstats import Stats
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate
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
from rest_framework.pagination import PageNumberPagination
from datetime import timedelta
from django.utils import timezone
from .utilities import validate_token, generate_token, staff_perm, sendMessage
import random


@api_view(['GET'])
def getUsers(request):
    token = request.data.get('token')
    if not staff_perm(token):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
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
    req_fields = ['email', 'phone', 'user_category', 'password']
    dict_info = request.data
    all_prs = True
    for field in req_fields:
        all_prs = all_prs and (field in dict_info)
    if all_prs:
        try:
            user = MyUser.objects.get(phone=request.data.get('phone'))
        except:
            user = None
        if user:
            return Response({"message": "A user with this phone already exists"},status=status.HTTP_400_BAD_REQUEST)

        try:
            user = MyUser(**dict_info)
            user.set_password(request.data.get('password'))
            user.save()
            payload = {
                    'phone': request.data.get('phone')
                }
            token = generate_token(payload)
            response = Response()
            response.data = {
                'token': token,
                'message': 'User created',
            }
            return response
        except:
            return Response(data={"message": "user not created"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data={"message": "required fields not present"},status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteUser(request, pk):    
    token = request.data.get('token')
    enc_info = validate_token(token)
    if not enc_info or pk != enc_info.get('phone'):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        user = MyUser.objects.get(phone=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()

    return Response({'message': 'User data deleted'})


@api_view(['GET'])
def getUser(request, pk):
    token = request.GET.get('token')
    enc_info = validate_token(token)
    if not enc_info or pk != enc_info.get('phone'):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        user = MyUser.objects.get(phone=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MyUserSerializer(user)

    return Response(serializer.data)

@api_view(['PUT'])
def updateUser(request, pk):
    dict_info = request.data
    token = dict_info.get('token')
    enc_info = validate_token(token)
    phone = enc_info.get('phone')
    if not enc_info or pk != phone:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    dict_info.pop('token')
    dict_info['phone'] = phone
    user = MyUser(**dict_info)
    if dict_info.get('password'):
        user.set_password(dict_info.get('password'))
    user.save()
    return Response(data={"message": "user updated"})

@api_view(['POST'])
def login(request):
    phone = int(request.data.get('phone'))
    try:
        user = MyUser.objects.get(phone=phone)
        password = request.data.get('password')
        
        if user.check_password(password):
            payload = {
                    'phone': phone
                }
            token = generate_token(payload)
            response = Response()
            response.data = {
                'token': token,
                'message': 'Logged in succesfully',
            }
            return response
        else :
            content = {'message': 'incorrect password'}
    except Exception as e:
        content = {'message': str(e)}

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
    otp = random.randint(100000,999999)
    sendMessage(phone, f'Your OTP is {otp}')
    newOTP = OTPModel(phone=phone, otp=otp)
    newOTP.save()
    return Response(data={"message": "OTP send"})


@api_view(['POST'])
def verifyOTP(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    print(phone, otp)
    if phone and otp:
        phone=int(phone)
        otp = str(otp)
        try:
            otp_row = OTPModel.objects.get(phone=phone)
        except:
            otp_row = None
        if otp_row:
            if (otp_row.otp == otp) and (otp_row.valid_until > timezone.now()): 
                otp_row.delete()  
                payload = {
                    'phone': phone
                }
                token = generate_token(payload)

                return Response(data={"token": token})

            return Response(data={"message": "OTP invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        
    return Response(status=status.HTTP_400_BAD_REQUEST)
