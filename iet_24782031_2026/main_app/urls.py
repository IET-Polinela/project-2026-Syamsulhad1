from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('reports/', views.ReportListView.as_view(), name='report_list'),
    path('reports/create/', views.ReportCreateView.as_view(), name='report_create'),
    path('reports/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('reports/update/<int:pk>/', views.ReportUpdateView.as_view(), name='report_update'),
    path('reports/delete/<int:pk>/', views.ReportDeleteView.as_view(), name='report_delete'),
    
    # Routing khusus untuk fungsi Update Status (Workflow)
    path('reports/status/<int:pk>/', views.ReportUpdateStatusView.as_view(), name='report_update_status'),
]