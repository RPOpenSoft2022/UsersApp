from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainSlidingView,
    TokenRefreshSlidingView,)

urlpatterns = [
	path('test/', views.testApi, name="test-api"),
	path('getusers/', views.getUsers, name="get-users"),
	path('createuser/', views.createUser, name="create-user"),
	path('deleteuser/<int:pk>/', views.deleteUser, name="delete-user"),
	path('getspecificuser/<int:pk>/', views.getSpecificUser, name="get-specific-user"),
	path('login/',views.login, name="login"),
	path('VerifyOTP/', views.VerifyOTP, name='token_obtain'),
]
