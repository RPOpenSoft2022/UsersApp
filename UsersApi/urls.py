from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,)

urlpatterns = [
	path('getusers/', views.getUsers, name="get-users"),
	path('signup/', views.createUser, name="create-user"),
	path('del-user/<int:pk>/', views.deleteUser, name="delete-user"),
	path('get-user/<int:pk>/', views.getUser, name="get-user"),
	path('update-user/<int:pk>/', views.updateUser, name="update-user"),
	path('login/',views.login, name="login"),
	path('verify-otp/', views.verifyOTP, name='verify-otp'),
	path('send-otp/', views.sendOTP, name='send-otp'),
]
