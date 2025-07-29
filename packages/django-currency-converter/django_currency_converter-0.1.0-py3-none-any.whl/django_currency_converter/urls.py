from django.urls import path
from .views import currency_view

urlpatterns = [
    path('convert/', currency_view, name='currency_converter'),
]
