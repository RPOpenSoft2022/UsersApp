from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('getusers/', views.getUsers, name="get-users"),
    path('signup/', views.createUser, name="create-user"),
    path('del-user/<int:pk>/', views.deleteUser, name="delete-user"),
    path('get-user/<int:pk>/', views.getUser, name="get-user"),
    path('update-user/<int:pk>/', views.updateUser, name="update-user"),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-otp/', views.verifyOTP, name='verify-otp'),
    path('send-otp/', views.sendOTP, name='send-otp'),
    path('logout/', views.BlacklistRefreshView.as_view(), name="logout"),
]
