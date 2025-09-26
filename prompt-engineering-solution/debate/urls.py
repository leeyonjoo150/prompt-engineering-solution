from django.urls import path
from . import views

app_name = 'debate'

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_session, name='create_session'),
    path('session/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('session/<uuid:session_id>/start/', views.start_debate, name='start_debate'),
    path('session/<uuid:session_id>/evaluate/', views.evaluate_debate, name='evaluate_debate'),
    path('sessions/', views.session_list, name='session_list'),
]