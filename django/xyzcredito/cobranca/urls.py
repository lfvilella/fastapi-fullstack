from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


app_name = 'cobranca'

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('cadastro/', views.CreateCobranca.as_view(), name='create'),
    path('devedores/', views.ListCobranca.as_view(), name='list'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
]
