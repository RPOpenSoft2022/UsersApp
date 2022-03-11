from django.urls import path
from . import views

urlpatterns = [
	path('test/', views.testApi, name="test-api"),
	path('getusers/', views.getUsers, name="get-users"),
	path('createuser/', views.createUser, name="create-user"),
	path('deleteuser/<int:pk>/', views.deleteUser, name="delete-user"),
	path('getspecificuser/<int:pk>/', views.getSpecificUser, name="get-specific-user"),
]
