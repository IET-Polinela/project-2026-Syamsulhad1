from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_app.urls')),      # Halaman Utama
    path('about/', include('about.urls')),   # Halaman Tentang Kota
    path('contacts/', include('contacts.urls')), # Halaman Kontak Darurat
    path('dashboard/', include('dashboard_24782031.urls')), # Dashboard Statistik
    # path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('usermanagement_24782031.urls')),
]
