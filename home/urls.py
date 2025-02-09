from django.urls import path
from . import views
from .views import explore_view, about_view, community_view, index_view, home_view

app_name = 'home'

urlpatterns = [
    path('index/', views.index_view, name='index'),
    path('home/', views.home_view, name='home'),
    path('explore/', explore_view, name='explore'),
    path('about/', about_view, name='about'),
    path('community/', community_view, name='community'),
    
]