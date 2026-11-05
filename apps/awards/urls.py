from django.urls import path
from . import views

app_name = 'awards'

urlpatterns = [
    path('', views.landing_view, name='list'),
]

