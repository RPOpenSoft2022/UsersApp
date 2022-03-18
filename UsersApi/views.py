from os import stat
from pstats import Stats
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .tokens import get_tokens_for_user
from .models import OTPModel
from .serializers import *
from rest_framework.views import APIView
from .models import User, UserManager
from datetime import date, datetime
import jwt
from rest_framework.pagination import PageNumberPagination
from datetime import timedelta
from django.utils import timezone
from .utilities import sendMessage, get_distance
import random
from rest_framework_simplejwt.tokens import RefreshToken
import pandas as pd

class BlacklistRefreshView(APIView):
    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("Logged out succesfully")


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    paginator = PageNumberPagination()
    if 'page_size' in request.GET:
        paginator.page_size = int(request.GET['page_size'])
    else:
        paginator.page_size = 10
    users = User.objects.all()
    result_page = paginator.paginate_queryset(users, request)
    serializer = UserSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['POST'])
def signUpView(request):
    user_data = request.data
    JWT_authenticator = JWTAuthentication()

    # authenticate() verifies and decode the token
    # if token is invalid, it raises an exception and returns 401
    try:
        response = JWT_authenticator.authenticate(request)
        user, token = response
    except:
        return Response(data={"message": "Your phone number is not verified!"}, status=status.HTTP_400_BAD_REQUEST)

    if user.customer:
        return Response(data={"message":"User with this phone number already exists"})

    serializer = CustomerSerializer(data=user_data, many=False)
    
    if serializer.is_valid():
        serializer.save(user=user)
        return Response({'messsge':'Successfully Signed Up! Head over to login'})
    else:
        return Response(data={"message": serializer.error_message()}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request, pk):
    JWT_authenticator = JWTAuthentication()

    # authenitcate() verifies and decode the token
    # if token is invalid, it raises an exception and returns 401
    response = JWT_authenticator.authenticate(request)
    user, token = response
    if user.id != pk:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        user = User.objects.get(phone=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()

    return Response({'message': 'User data deleted'})

# accept id of User table
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request, pk):
    JWT_authenticator = JWTAuthentication()

    # authenitcate() verifies and decode the token
    # if token is invalid, it raises an exception and returns 401
    response = JWT_authenticator.authenticate(request)
    user, token = response
    if user.id != pk:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        user = User.objects.get(phone=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(user)

    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    JWT_authenticator = JWTAuthentication()

    # authenitcate() verifies and decode the token
    # if token is invalid, it raises an exception and returns 401
    response = JWT_authenticator.authenticate(request)
    user, token = response
    if user.id != pk:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    dict_info = request.data

    try:
        dict_info.pop('password')
    except:
        pass

    try:
        for attr, value in dict_info.items(): 
            setattr(user, attr, value)
        user.save()
        return Response(data={"message": "user updated"})
    except:
        return Response(data={"message":"user not updated"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def sendOTP(request):
    phone = request.data.get('phone')

    try:
        otp_row = OTPModel.objects.get(phone=phone)
    except:
        otp_row = None

    if otp_row:
        if otp_row.valid_until > timezone.now():
            return Response(data={"message": "OTP already sent"})
        otp_row.delete()
    otp = random.randint(100000,999999)
    try:
        try:
            sendMessage(phone, f'Your OTP is {otp}')
        except Exception as e:
            return Response(data={"message": "Couldn't send OTP"}, status=status.HTTP_400_BAD_REQUEST)
        newOTP = OTPModel(phone=phone, otp=otp)
        newOTP.save()
        return Response(data={"message": "OTP send"})
    except:
        return Response(data={"message":"OTP not send"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verifyOTP(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    newPassword = request.data.get('newPassword')
    print(newPassword)
    if phone and otp:
        phone = int(phone)
        otp = str(otp)
        try:
            otp_row = OTPModel.objects.get(phone=phone)
        except:
            otp_row = None
        if otp_row:
            if (otp_row.otp == otp) and (otp_row.valid_until > timezone.now()):
                otp_row.delete()
                message = "Some message"
                try: 
                    user = User.objects.get(phone=phone)
                    if newPassword:
                        user.set_password(newPassword)
                        user.save()
                        message = "Password Updated"
                    else:
                        message = "Send New Password"
                except User.DoesNotExist:
                    try:
                        user = User.objects.create(phone=phone)
                        user.set_password(newPassword)
                        user.save()
                        message = "Login credentials created"
                    except Exception as e:
                        return Response({"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)

                token = get_tokens_for_user(user)

                return Response(data={"token": token, "message": message})

            return Response(data={"message": "OTP invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(data={"message": "First generate OTP!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def addEmployee(request, pk):
    if pk not in ['Staff', 'Delivery']:
        return Response(data={"message": "Invalid User Category!"}, status=status.HTTP_400_BAD_REQUEST)
        
    sheet = request.FILES['sheet']
    df = pd.read_csv(sheet)
    for index, row in df.iterrows():
        print(row["phone"])
        user = User.objects.create(phone=row["phone"], email=row["email"], user_category = pk)
        user.set_password(row["password"])
        user.save()
    return Response({"message": f"Added {pk} data succesfully!"})
