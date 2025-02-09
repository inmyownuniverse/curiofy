from django.db import models
from accounts.models import CustomUser

class Quiz(models.Model):
    QUIZ_TYPES = [
        ('normal', 'Normal Quiz'),
        ('voice', 'Voice Quiz'),
    ]
    
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    quiz_type = models.CharField(max_length=10, choices=QUIZ_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.quiz_type})"
    
    @property
    def total_questions(self):
        return self.questions.count()

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_answer = models.CharField(max_length=200)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')

    def __str__(self):
        return self.question_text[:50]

class QuizResult(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    quiz_type = models.CharField(max_length=10, choices=Quiz.QUIZ_TYPES)

    class Meta:
        ordering = ['-score', '-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"


