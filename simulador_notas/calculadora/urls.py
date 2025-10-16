from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('ramo/<int:ramo_id>/', views.calculadora_ramo, name='calculadora'),
    path('ramo/<int:ramo_id>/', views.calculadora_ramo, name='calculadora'),
]
