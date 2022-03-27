from email import message
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
from datetime import date, datetime, timedelta
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from .utilities import sendMessage
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
def register(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    password = request.data.get('password')
    if phone and otp and password:
        user = User.objects.filter(phone=phone).first()
        if user:
            return Response(data={"message":"User with this phone already exists."}, status=status.HTTP_400_BAD_REQUEST)
        phone = int(phone)
        otp = str(otp)
        otp_row = OTPModel.objects.filter(phone=phone).first()
        if otp_row:
            if (otp_row.otp == otp) and (otp_row.valid_until > timezone.now()):
                otp_row.delete()
                try:
                    user = User.objects.create(phone=phone)
                    user.set_password(password)
                    user.save()
                    token = get_tokens_for_user(user)
                    return Response(data={**token, "message": "User is registered."})
                except Exception as e:
                    return Response({"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message":"OTP is invalid."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"message":"Generate OTP first!"}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(data={"message":"Required fields not present"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteUser(request):
    JWT_authenticator = JWTAuthentication()
    response = JWT_authenticator.authenticate(request)
    user, token = response
    user.delete()
    return Response({'message': 'User deleted'})

# accept id of User table
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUser(request):
    JWT_authenticator = JWTAuthentication()
    response = JWT_authenticator.authenticate(request)
    user, token = response

    serializer = UserSerializer(user)

    try:
        customer = user.customer
    except:
        customer = None
    if user.user_category == 'Customer' and customer:
        return Response({**serializer.data, **CustomerSerializer(customer).data})

    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request):
    JWT_authenticator = JWTAuthentication()
    response = JWT_authenticator.authenticate(request)
    user, token = response
    dict_info = request.data.copy()

    try:
        dict_info.pop('password')
    except:
        pass
   
    try:
        if dict_info.get('phone'):
            setattr(user, 'phone', dict_info.get('phone'))
    
        if dict_info.get('email'):
            setattr(user, 'email', dict_info.get('email'))

        try:
            serializer = CustomerSerializer(instance=user.customer, data=dict_info, many=False)
        except:
            serializer = CustomerSerializer(data=dict_info, many=False)
    
        if serializer.is_valid():
            serializer.save(user=user)
            user.save()
            return Response({'message':'User info saved'})
        return Response(data={"message":str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response(data={"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    otp = random.randint(1000,9999)
    try:
        try:
            sendMessage(phone, f'Your OTP is {otp}')
        except Exception as e:
            return Response(data={"message": "Couldn't send OTP"}, status=status.HTTP_400_BAD_REQUEST)
        newOTP = OTPModel(phone=phone, otp=otp)
        newOTP.save()
        return Response(data={"message": "OTP sent"})
    except:
        return Response(data={"message":"OTP not sent"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def resetPassword(request):
    phone = request.data.get('phone')
    otp = request.data.get('otp')
    new_password = request.data.get('new_password')
    if phone and otp and new_password:
        phone = int(phone)
        otp = str(otp)
        otp_row = OTPModel.objects.filter(phone=phone).first()
        if otp_row:
            if (otp_row.otp == otp) and (otp_row.valid_until > timezone.now()):
                otp_row.delete()
                try: 
                    user = User.objects.get(phone=phone)
                    user.set_password(new_password)
                    user.save()
                except User.DoesNotExist:
                    return Response(data={"message":"User does not exist."}, status=status.HTTP_400_BAD_REQUEST)

                token = get_tokens_for_user(user)
                return Response(data={**token, "message": "Password Updated"})

            return Response(data={"message": "OTP invalid!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"message": "First generate OTP!"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message":"Required fields not present!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def addEmployee(request, pk):
    if pk not in ['Staff', 'Delivery']:
        return Response(data={"message": "Invalid User Category!"}, status=status.HTTP_400_BAD_REQUEST)
        
    sheet = request.FILES['sheet']
    df = pd.read_csv(sheet)
    for index, row in df.iterrows():
        user = User.objects.create(phone=row["phone"], email=row["email"], user_category = pk)
        user.set_password(row["password"])
        user.save()
    return Response({"message": f"Added {pk} data succesfully!"})


@api_view(['POST'])
def closestDeliveryPartner(request):
    location = request.data['pickup_location']
    print(location)
    return JsonResponse({"loc": location, "partner_user_id": 1})