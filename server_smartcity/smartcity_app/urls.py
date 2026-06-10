from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from usermanagement_24782031.api_views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('', include('main_app.urls')),      # Halaman Utama
    path('about/', include('about.urls')),   # Halaman Tentang Kota
    path('contacts/', include('contacts.urls')), # Halaman Kontak Darurat
    path('dashboard/', include('dashboard_24782031.urls')), # Dashboard Statistik
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('usermanagement_24782031.urls')),
    path('api/', include('main_app.api_urls')), # API Endpoint untuk Laporan
]
