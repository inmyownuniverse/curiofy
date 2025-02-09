from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('get_started/', views.get_started, name='get_started'),
    path('science/', views.science, name='science'),
    path('mathematics/', views.mathematics, name='mathematics'),
    path('engineering/', views.engineering, name='engineering'),
    path('technology/', views.technology, name='technology'),  

]
