from django.urls import path
from . import views

urlpatterns = [
    # path('', views.abc)
    path('recommendations/<str:user_id>/', views.get_recommendations.as_view())
]
