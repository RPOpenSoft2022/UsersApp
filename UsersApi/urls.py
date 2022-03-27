from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
	TokenVerifyView,
)

urlpatterns = [
	path('getusers/', views.getUsers, name="get-users"),
	path('del-user/', views.deleteUser, name="delete-user"),
	path('get-user/', views.getUser, name="get-user"),
	path('update-user/', views.updateUser, name="update-user"),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
	path('reset-password/', views.resetPassword, name='reset-password'),
	path('send-otp/', views.sendOTP, name='send-otp'),
	path('logout/', views.BlacklistRefreshView.as_view(), name="logout"),
	path('register/', views.register, name="register"),
	path('add/<str:pk>/', views.addEmployee, name="addEmployees"),
	path('usershistory', views.usershistory, name="usersHistory"),
]
