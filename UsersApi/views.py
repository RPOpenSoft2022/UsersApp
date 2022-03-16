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
def createUser(request):
    req_fields = ['email', 'phone', 'password']
    dict_info = request.data
    try:
        dict_info.pop('user_category')
    except:
        pass
    
    all_prs = True
    for field in req_fields:
        all_prs = all_prs and (field in dict_info)
    if all_prs:
        try:
            user = User.objects.get(phone=request.data.get('phone'))
        except:
            user = None
        if user:
            return Response({"message": "A user with this phone already exists"},status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User(**dict_info)
            user.set_password(request.data.get('password'))
            user.save()
            response = Response()
            response.data = {
                'message': 'User created, now you can login',
            }
            return response
        except:
            return Response(data={"message": "user not created"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data={"message": "required fields not present"},status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signUpView(request):
    user_data = request.data['user_data']
    customer_data = request.data['customer_data']

    # user_data.pop('password1')
    # user_data.pop('password2')
    if 'user_category' in user_data:
        user_data.pop('user_category')

    serializer = UserSerializer(data=user_data, many=False)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(phone = user_data["phone"])

        if user_data["password1"] != user_data["password2"]:
            return Response({"message":"Passwords didn't match"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(request.data['user_data']["password1"])
        user.save()
    else:
        return Response(data={"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    serializer = CustomerSerializer(data=customer_data, many=False)
    if serializer.is_valid():
        serializer.save()
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
    user , token = response
    if user.phone != pk:
        return Response(status=status.HTTP_401_UNAUTHORIZED)   
    try:
        user = User.objects.get(phone=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user.delete()

    return Response({'message': 'User data deleted'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request, pk):    
    JWT_authenticator = JWTAuthentication()

    # authenitcate() verifies and decode the token
    # if token is invalid, it raises an exception and returns 401
    response = JWT_authenticator.authenticate(request)
    user , token = response
    if user.phone != pk:
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
    user , token = response
    if user.phone != pk:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    dict_info = request.data

    try:
        dict_info.pop('password')
    except:
        pass

    try:
        for attr, value in dict_info.items(): 
            setattr(user, attr, value)
        # if dict_info.get('password'):
        #     user.set_password(dict_info.get('password'))
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
        sendMessage(phone, f'Your OTP is {otp}')
        newOTP = OTPModel(phone=phone, otp=otp)
        newOTP.save()
        return Response(data={"message": "OTP send"})
    except:
        return Response(data={"message":"OTP not send"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verifyOTP(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
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
                user = User.objects.get(phone=phone)
                token = get_tokens_for_user(user)

                return Response(data={"token": token})

            return Response(data={"message": "OTP invalid"}, status=status.HTTP_401_UNAUTHORIZED)
        
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nearest_delivery(request):
    lat = float(request.data.get('lat'))
    long = float(request.data.get('long'))

    delivery_users = User.objects.filter(user_category='Delivery').filter(is_free=True)
    nr_dist = -1
    phone_nearest = None
    for user in delivery_users:
        ps_dist = get_distance((lat, long), (user.current_lat, user.current_long))
        if (nr_dist == -1) or (nr_dist > ps_dist):
            
            nr_dist = ps_dist
            phone_nearest = user.phone

    if nr_dist == -1:
        return Response({"message": "No delivery partners free"})
    return Response({"delivery_phone": phone_nearest})

