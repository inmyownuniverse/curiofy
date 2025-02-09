from django.contrib import admin
from .models import Quiz, Question, QuizResult

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'quiz_type', 'created_at')
    list_filter = ('subject', 'quiz_type')
    search_fields = ('title', 'subject')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'difficulty', 'correct_answer')
    list_filter = ('quiz__subject', 'quiz__quiz_type', 'difficulty')
    search_fields = ('question_text', 'quiz__title')

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'quiz_type', 'completed_at')
    list_filter = ('quiz_type', 'quiz__subject')
    search_fields = ('user__username', 'quiz__title')

