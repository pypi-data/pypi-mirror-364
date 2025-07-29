from django.urls import path
from .views import personalized_visit_view

app_name = 'django_visit_counter'

urlpatterns = [
    path('', personalized_visit_view, name='personalized'),
]
