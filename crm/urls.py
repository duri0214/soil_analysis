from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'crm'
urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('company/list', views.CompanyListView.as_view(), name='company_list'),
    path('company/create', views.CompanyCreateView.as_view(), name='company_create'),
    path('company/<int:pk>/detail', views.CompanyDetailView.as_view(), name='company_detail'),
    path('company/<int:company_id>/land/list', views.LandListView.as_view(), name='land_list'),
    path('company/<int:company_id>/land/create', views.LandCreateView.as_view(), name='land_create'),
    path('company/<int:company_id>/land/<int:pk>/detail', views.LandDetailView.as_view(), name='land_detail'),
    path('company/<int:company_id>/landledger/<int:landledger_id>/land_report_chemical',
         views.LandReportChemicalListView.as_view(), name='land_report_chemical'),
    path('upload/soilhardness', views.UploadSoilhardnessView.as_view(), name='upload_soilhardness'),
    path('upload/success/', views.UploadZipSuccessView.as_view(), name='upload_soilhardness_success'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
