from django.urls import path
from . import views

urlpatterns = [
    path('api/', views.recommend_properties2, name='recommend_properties'),
]
