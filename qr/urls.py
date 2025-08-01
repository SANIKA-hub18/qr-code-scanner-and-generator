# qr/urls.py

from django.urls import path
from .views import QrCodeView, QrCodeScan

app_name = 'qr'  

urlpatterns = [
    path('', QrCodeView.as_view(), name='qr_code_view'),
    path('scan/', QrCodeScan.as_view(), name='qrscan'),  
]
