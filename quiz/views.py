from django.shortcuts import render, redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .voice_quiz import VoiceQuizSystem, QuizManager, VoiceQuiz
from .models import Quiz, Question, QuizResult
import json

@login_required
def start_quiz(request):
    # Get unique subjects from voice quizzes only
    subjects = Quiz.objects.filter(quiz_type='voice').values_list('subject', flat=True).distinct()
    
    # Get difficulties from the Question model choices
    difficulties = [choice[0] for choice in Question.DIFFICULTY_CHOICES]
    
    # Print for debugging
    print("Categories:", list(subjects))
    print("Difficulties:", difficulties)
    
    context = {
        'categories': subjects,
        'difficulties': difficulties
    }
    
    if request.method == 'POST':
        try:
            category = request.POST.get('category')
            difficulty = request.POST.get('difficulty')
            
            # Debug prints
            print(f"Starting quiz - Category: {category}, Difficulty: {difficulty}")
            
            # Check if questions exist before starting
            questions_exist = Question.objects.filter(
                quiz__quiz_type='voice',
                quiz__subject=category,
                difficulty=difficulty
            ).exists()
            
            if not questions_exist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No questions available for the selected category and difficulty'
                })
            
            quiz = VoiceQuizSystem(request.user)
            quiz.run_quiz(category, difficulty)
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            print(f"Error in start_quiz view: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return render(request, 'quiz/start_quiz.html', context)

@login_required
def leaderboard(request):
    quiz_type = request.GET.get('quiz_type', 'all')
    subject = request.GET.get('subject', 'all')
    
    results = QuizResult.objects.select_related('user', 'quiz').all()
    
    if quiz_type != 'all':
        results = results.filter(quiz_type=quiz_type)
    if subject != 'all':
        results = results.filter(quiz__subject=subject)
    
    subjects = Quiz.objects.values_list('subject', flat=True).distinct()
    
    return render(request, 'quiz/leaderboard.html', {
        'results': results,
        'subjects': subjects
    })

@login_required
def quiz_view(request):
    if request.method == 'POST':
        try:
            category = request.POST.get('category')
            difficulty = request.POST.get('difficulty')
            
            # Get questions based on category and difficulty
            questions = Question.objects.filter(
                category=category,
                difficulty=difficulty
            )
            
            if not questions.exists():
                return JsonResponse({
                    'error': 'No questions found for the selected category and difficulty'
                }, status=404)
                
            # Convert questions to JSON format
            questions_data = list(questions.values('id', 'question_text', 'options', 'correct_answer'))
            
            return JsonResponse({
                'questions': questions_data
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
            
    return render(request, 'quiz/quiz.html')

@login_required
def quiz_selection(request):
    return render(request, 'quiz/quiz_selection.html')

@login_required
def normal_quiz(request):
    # Get all normal quizzes
    quizzes = Quiz.objects.filter(quiz_type='normal')
    current_quiz = None
    questions = []
    
    if request.method == 'POST':
        quiz_id = request.POST.get('quiz_id')
        if quiz_id:
            current_quiz = Quiz.objects.get(id=quiz_id)
            questions = Question.objects.filter(quiz=current_quiz)
    
    context = {
        'quizzes': quizzes,
        'current_quiz': current_quiz,
        'questions': questions,
    }
    return render(request, 'quiz/normal_quiz.html', context)

@login_required
def submit_quiz(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', {})
        
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        
        score = 0
        total_questions = len(questions)
        
        for question in questions:
            user_answer = answers.get(str(question.id))
            if user_answer == question.correct_answer:
                score += 1
        
        percentage = int((score / total_questions) * 100)
        
        # Save quiz result
        QuizResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=percentage,
            quiz_type='normal'
        )
        
        return JsonResponse({
            'score': percentage,
            'total_questions': total_questions,
            'correct_answers': score
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def start_voice_quiz(request):
    quiz_manager = QuizManager()
    # Start the quiz and voice recognition
    questions = generate_quiz_questions('python', 5)
    quiz_manager.start_quiz(questions)
    quiz_manager.voice_quiz.start_listening()
    
    # Return first question
    return JsonResponse({
        'question': quiz_manager.next_question()
    })

# Create your views here.
