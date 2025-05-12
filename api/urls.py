from django.urls import path
from .views import ChatAPIView

urlpatterns = [
    path('studio/', ChatAPIView.as_view(), name='studio'),
]