from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,)

urlpatterns = [
	path('getusers/', views.getUsers, name="get-users"),
	path('signup/', views.createUser, name="create-user"),
	path('user/<int:pk>/', views.deleteUser, name="delete-user"),
	path('user/<int:pk>/', views.getSpecificUser, name="get-specific-user"),
	path('login/',views.login, name="login"),
	path('verify-otp/', views.verifyOTP, name='verify-otp'),
	path('send-otp/', views.sendOTP, name='send-otp'),
]
