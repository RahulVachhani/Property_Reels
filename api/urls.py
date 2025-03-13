from django.urls import path
from . import views
# from . import views1

urlpatterns = [
    path('', views.FindReel.as_view())
]
