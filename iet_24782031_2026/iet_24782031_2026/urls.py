from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def welcome_view(request):
    return HttpResponse("Selamat Datang DI Web Django Syamsul Hadi")

urlpatterns = [
    # Ganti 'admin.site.safe_urls' menjadi 'admin.site.urls'
    path('admin/', admin.site.urls), 
    path('welcome/', welcome_view),
]