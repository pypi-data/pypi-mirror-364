# convert_aram/urls.py

from django.urls import path
from .views import *

app_name= "convert_aram"

urlpatterns = [
    path('', converter_form, name='converter'),
    path('result/',converter_results, name='resultat')
]
