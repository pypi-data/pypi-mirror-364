from django.urls import path
from .views import checker_view

urlpatterns = [
    path('', checker_view, name='checker'),
]
