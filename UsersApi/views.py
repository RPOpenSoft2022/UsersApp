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
from .serializers import MyUserSerializer
from rest_framework.views import APIView
from .models import MyUser, MyUserManager
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
    users = MyUser.objects.all()
    result_page = paginator.paginate_queryset(users, request)
    serializer = MyUserSerializer(result_page, many=True)
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
            user = MyUser.objects.get(phone=request.data.get('phone'))
        except:
            user = None
        if user:
            return Response({"message": "A user with this phone already exists"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = MyUser(**dict_info)
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
        return Response(data={"message": "required fields not present"}, status=status.HTTP_400_BAD_REQUEST)


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
        user = MyUser.objects.get(id=pk)
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
    user, token = response
    if user.id != pk:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        user = MyUser.objects.get(id=pk)
    except Exception as e:
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MyUserSerializer(user)

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
        return Response(data={"message": "user not updated"}, status=status.HTTP_400_BAD_REQUEST)


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
    otp = random.randint(100000, 999999)
    try:
        sendMessage(phone, f'Your OTP is {otp}')
        newOTP = OTPModel(phone=phone, otp=otp)
        newOTP.save()
        return Response(data={"message": "OTP send"})
    except:
        return Response(data={"message": "OTP not send"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verifyOTP(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    newPassword = request.data.get('new-password')
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
                user = MyUser.objects.get(phone=phone)
                if newPassword:
                    user.set_password(newPassword)
                user.save()
                token = get_tokens_for_user(user)

                return Response(data={"token": token, "message": "Password updated"})

            return Response(data={"message": "OTP invalid"}, status=status.HTTP_401_UNAUTHORIZED)

    return Response(status=status.HTTP_400_BAD_REQUEST)