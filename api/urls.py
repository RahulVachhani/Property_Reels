from django.urls import path
from . import views

urlpatterns = [
    path('', views.FindReel.as_view())
]
