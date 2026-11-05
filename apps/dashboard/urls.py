from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview_view, name='overview'),
    path('toggle-period/', views.toggle_period_view, name='toggle_period'),
    path('categories/', views.categories_view, name='categories'),
    path('nominations/', views.nominations_view, name='nominations'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('name-review/', views.name_review_view, name='name_review'),
]

