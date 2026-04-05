from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/create/', views.report_create, name='report_create'),
    path('reports/update/<int:pk>/', views.report_update, name='report_update'),
    path('reports/delete/<int:pk>/', views.report_delete, name='report_delete'),
]