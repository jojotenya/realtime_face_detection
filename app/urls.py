from django.urls import path
from . import views

urlpatterns = [
    path('', views.livestream, name='livestream'),
]
