from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_selection, name='quiz_selection'),
    path('normal/', views.normal_quiz, name='normal_quiz'),
    path('start/', views.start_quiz, name='start_quiz'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('submit/', views.submit_quiz, name='submit_quiz'),
]