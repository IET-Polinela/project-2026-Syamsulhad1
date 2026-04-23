from django.urls import path
from django.shortcuts import redirect
from .views import CustomLoginView, CustomLogoutView, register_view

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', lambda request: redirect('home'), name='profile'),
]