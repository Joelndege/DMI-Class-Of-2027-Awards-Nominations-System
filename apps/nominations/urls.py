from django.urls import path
from . import views

app_name = 'nominations'

urlpatterns = [
    path('', views.wizard_view, name='wizard'),
    path('save-draft/', views.save_draft_entry_view, name='save_draft'),
    path('review/', views.review_view, name='review'),
    path('submit/', views.submit_view, name='submit'),
    path('success/', views.success_view, name='success'),
]

