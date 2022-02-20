from django.urls import path

from comparator.views import recognize

urlpatterns = [
    path('check', recognize.as_view(), name='check'),
]