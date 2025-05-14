import speech_recognition as sr
import json
import random
import time
from threading import Thread, Event
import logging
from django.db import transaction
from .models import Quiz, Question, QuizResult
import pyttsx3

class VoiceQuiz:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # List available microphones
        mics = sr.Microphone.list_microphone_names()
        print(f"Available microphones: {mics}")
        
        # Adjust recognition parameters
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 4000
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = None
        
        self.stop_event = Event()
        self.current_answer = None
        self.is_listening = False
        
        self.timeout_count = 0
        self.max_timeouts = 3
        
    def start_listening(self):
        """Start listening for voice input"""
        try:
            self.is_listening = True
            self.stop_event.clear()
            
            # Create a new microphone instance for each listening session
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Adjusted for ambient noise")
            
            def listen_loop():
                while not self.stop_event.is_set():
                    try:
                        with sr.Microphone() as source:
                            print("Listening for input...")
                            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                            self.timeout_count = 0
                            
                            try:
                                text = self.recognizer.recognize_google(audio)
                                self.current_answer = text.lower()
                                print(f"Recognized: {text}")
                                return
                            except sr.UnknownValueError:
                                print("Could not understand audio")
                            except sr.RequestError as e:
                                print(f"Could not request results; {e}")
                    except Exception as e:
                        print(f"Error in listen loop: {e}")
                        self.timeout_count += 1
                        if self.timeout_count >= self.max_timeouts:
                            print("Max timeouts reached, stopping listen loop")
                            self.stop_event.set()
                            return
                        time.sleep(0.1)
            
            self.listen_thread = Thread(target=listen_loop)
            self.listen_thread.daemon = True
            self.listen_thread.start()
        except Exception as e:
            print(f"Error in start_listening: {e}")
            raise
    
    def stop_listening(self):
        """Stop listening for voice input"""
        self.stop_event.set()
        self.is_listening = False
        self.current_answer = None
    
    def check_answer(self, expected_answer):
        """Check if the current answer matches the expected answer"""
        if not self.current_answer:
            return False
            
        # Convert both to lowercase and strip whitespace
        current = self.current_answer.lower().strip()
        expected = expected_answer.lower().strip()
        
        # Check for exact match or close match
        return current == expected or current in expected or expected in current
    
    def get_current_answer(self):
        """Get the current recognized answer"""
        return self.current_answer
    
    def is_active(self):
        """Check if voice recognition is active"""
        return self.is_listening

    def reset(self):
        """Reset the voice recognition state"""
        self.stop_event.set()
        time.sleep(0.5)  # Give time for the previous thread to stop
        self.stop_event.clear()
        self.current_answer = None
        self.is_listening = False
        self.timeout_count = 0

class QuizManager:
    def __init__(self):
        self.voice_quiz = VoiceQuiz()
        self.current_question = None
        self.score = 0
        self.total_questions = 0
        
    def start_quiz(self, questions):
        """Start a new quiz with given questions"""
        self.questions = questions
        self.score = 0
        self.total_questions = len(questions)
        self.current_question = None
        
    def next_question(self):
        """Get the next question"""
        if not self.questions:
            return None
        self.current_question = self.questions.pop(0)
        return self.current_question
        
    def check_answer(self, answer):
        """Check if the answer is correct"""
        if not self.current_question:
            return False
            
        correct_answer = self.current_question['answer'].lower().strip()
        user_answer = answer.lower().strip()
        
        if user_answer == correct_answer:
            self.score += 1
            return True
        return False
        
    def get_score(self):
        """Get current score"""
        return {
            'score': self.score,
            'total': self.total_questions
        }

# Helper functions for quiz generation
def generate_quiz_questions(topic, num_questions=5):
    """Generate quiz questions for a given topic"""
    # This is a placeholder - you should implement actual question generation
    sample_questions = [
        {
            'question': 'What is Python?',
            'answer': 'programming language'
        },
        {
            'question': 'What is Django?',
            'answer': 'web framework'
        }
    ]
    return random.sample(sample_questions, min(num_questions, len(sample_questions)))

def format_question(question_data):
    """Format a question for display"""
    return {
        'question': question_data['question'],
        'answer': question_data['answer']
    }

class VoiceQuizSystem:
    def __init__(self, user):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.score = 0
        self.total_questions = 0
        self.user = user
        self.quiz_manager = QuizManager()
        self.waiting_for_answer = False
        
    def speak(self, text):
        print(f"Speaking: {text}")  # Debug print
        self.engine.say(text)
        self.engine.runAndWait()
                
    def get_questions(self, category=None, difficulty=None):
        try:
            # Start with questions from voice quizzes only
            query = Question.objects.filter(quiz__quiz_type='voice')
            
            if category:
                query = query.filter(quiz__subject=category)
            if difficulty:
                query = query.filter(difficulty=difficulty)
            
            questions = list(query.order_by('?')[:5])  # Get 5 random questions
            
            if not questions:
                raise ValueError(f"No questions found for {category} - {difficulty}")
            
            print(f"Found {len(questions)} questions for {category} - {difficulty}")  # Debug print
            
            if questions:
                self.current_quiz = questions[0].quiz
            
            return questions
        except Exception as e:
            print(f"Error in get_questions: {str(e)}")
            raise
        
    def run_quiz(self, category=None, difficulty=None):
        self.speak(f"Welcome {self.user.username} to the Voice Quiz!")
        questions = self.get_questions(category, difficulty)
        self.total_questions = len(questions)
        
        # Store the quiz object for later use
        self.current_quiz = questions[0].quiz if questions else None
        
        self.quiz_manager.start_quiz(questions)
        
        for question in questions:
            # Read question and options
            self.speak(question.question_text)
            time.sleep(0.5)
            self.speak(f"Option 1: {question.option1}")
            time.sleep(0.3)
            self.speak(f"Option 2: {question.option2}")
            time.sleep(0.3)
            self.speak(f"Option 3: {question.option3}")
            time.sleep(0.3)
            self.speak(f"Option 4: {question.option4}")
            
            answer_received = False
            max_attempts = 3
            attempts = 0
            
            while not answer_received and attempts < max_attempts:
                self.speak("Please speak your answer number")
                self.waiting_for_answer = True
                self.quiz_manager.voice_quiz.reset()  # Reset voice recognition state
                self.quiz_manager.voice_quiz.start_listening()
                
                # Wait for answer with timeout
                wait_time = 0
                while self.quiz_manager.voice_quiz.is_active() and wait_time < 10:
                    time.sleep(0.1)
                    wait_time += 0.1
                    user_answer = self.quiz_manager.voice_quiz.get_current_answer()
                    if user_answer:
                        break
                
                user_answer = self.quiz_manager.voice_quiz.get_current_answer()
                self.waiting_for_answer = False
                
                if user_answer:
                    # Enhanced answer mapping with more variations
                    answer_map = {
                        # First/1/One variations
                        'one': 1, 'won': 1, 'first': 1, 'number one': 1, 'option one': 1,
                        'option 1': 1, 'number 1': 1, 'answer one': 1, 'answer 1': 1,
                        '1': 1,
                        
                        # Second/2/Two variations
                        'two': 2, 'too': 2, 'to': 2, 'second': 2, 'number two': 2,
                        'option two': 2, 'option 2': 2, 'number 2': 2, 'answer two': 2,
                        'answer 2': 2, '2': 2,
                        
                        # Third/3/Three variations
                        'three': 3, 'third': 3, 'number three': 3, 'option three': 3,
                        'option 3': 3, 'number 3': 3, 'answer three': 3, 'answer 3': 3,
                        '3': 3,
                        
                        # Fourth/4/Four variations
                        'four': 4, 'for': 4, 'fourth': 4, 'number four': 4,
                        'option four': 4, 'option 4': 4, 'number 4': 4, 'answer four': 4,
                        'answer 4': 4, '4': 4,
                        # Additional variations for common misrecognitions
                        'caption one': 1, 'caption 1': 1,
                        'caption two': 2, 'caption 2': 2,
                        'caption three': 3, 'caption 3': 3,
                        'caption four': 4, 'caption 4': 4, 'caption for': 4
                    }
                    
                    # Clean up the answer and convert to lowercase
                    user_answer = user_answer.strip().lower()
                    print(f"Processing answer: {user_answer}")  # Debug print
                    
                    # Try to map the answer to a number
                    mapped_answer = answer_map.get(user_answer)
                    print(f"Mapped to: {mapped_answer}")  # Debug print
                    
                    if mapped_answer is not None:
                        answer_received = True
                        self.quiz_manager.voice_quiz.stop_listening()  # Stop listening after getting answer
                        
                        if int(mapped_answer) == int(question.correct_answer):
                            self.speak("Correct answer!")
                            self.score += 1
                        else:
                            self.speak(f"Wrong answer! The correct answer was option {question.correct_answer}")
                        time.sleep(1)  # Give time for the response before next question
                    else:
                        self.speak("Please say a number between 1 and 4")
                
                attempts += 1
                if not answer_received:
                    self.quiz_manager.voice_quiz.stop_listening()
                
            if not answer_received:
                self.speak("Moving to the next question")
                time.sleep(1)
        
        self.end_quiz()
        
    def end_quiz(self):
        percentage = (self.score / self.total_questions) * 100
        self.speak(f"Quiz completed! Your score is {self.score} out of {self.total_questions}")
        self.speak(f"That's {percentage:.1f} percent!")
        
        # Save attempt to database
        with transaction.atomic():
            QuizResult.objects.create(
                user=self.user,
                quiz=self.current_quiz,  # Use the stored quiz object
                score=self.score,
                quiz_type='voice'
            )
        
        # Display leaderboard
        self.display_leaderboard()
        
    def display_leaderboard(self):
        top_scores = QuizResult.objects.select_related('user', 'quiz').order_by('-score')[:5]
        
        self.speak("Top 5 scores:")
        for result in top_scores:
            total = result.quiz.questions.count()  # Get the count directly
            self.speak(f"{result.user.username} scored {result.score} out of {total}")

    def process_quiz_attempt(self, user, quiz, answers):
        score = sum(1 for a in answers if a['correct'])
        
        # Save quiz result
        QuizResult.objects.create(
            user=user,
            quiz=quiz,
            score=score,
            quiz_type='voice'
        )
        
        return score