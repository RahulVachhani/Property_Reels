from django.urls import path
from . import views

urlpatterns = [
    path('recommendations/<int:user_id>/', views.ReelRecommendationView.as_view()),
    path('like-reel/', views.LikeReel.as_view()),
    path('search/', views.SearchReel.as_view())
]
