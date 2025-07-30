from django.urls import path
from .views import phonecode_view

urlpatterns = [
    path('phonecode/', phonecode_view, name='phonecode'),
]
