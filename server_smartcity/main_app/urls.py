from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/search/', views.report_search, name='report_search'),
    path('reports/data/', views.ReportListJsonView.as_view(), name='report_list_json'),
    path('reports/<int:pk>/data/', views.ReportDetailJsonView.as_view(), name='report_detail_json'),
    path('reports/<int:pk>/api/', views.report_detail_api, name='report_detail_api'),
    path('reports/create/', views.ReportCreateView.as_view(), name='report_create'),
    path('reports/create/', views.ReportCreateView.as_view(), name='add_report'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('reports/update/<int:pk>/', views.ReportUpdateView.as_view(), name='report_update'),
    path('reports/update/<int:pk>/', views.ReportUpdateView.as_view(), name='update_report'),
    path('reports/delete/<int:pk>/', views.ReportDeleteView.as_view(), name='report_delete'),
    path('reports/delete/<int:pk>/', views.ReportDeleteView.as_view(), name='delete_report'),
    
    # Routing khusus untuk fungsi Update Status (Workflow)
    path('reports/status/<int:pk>/', views.ReportUpdateStatusView.as_view(), name='report_update_status'),
    path('reports/status/<int:pk>/', views.update_status, name='update_status'),
    path('reports/status/<int:pk>/<str:new_status>/', views.update_status, name='update_status'),
]
