from django.urls import path
from . import views

urlpatterns = [
	path('test/', views.testApi, name="test-api"),
]
