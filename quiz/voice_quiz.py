import pyttsx3
import speech_recognition as sr
from django.db import transaction
from .models import Quiz, Question, QuizResult
import time

class VoiceQuizSystem:
    def __init__(self, user):
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.score = 0
        self.total_questions = 0
        self.user = user
        self.mic = sr.Microphone()
        
    def speak(self, text):
        print(f"Speaking: {text}")  # Debug print
        self.engine.say(text)
        self.engine.runAndWait()
        
    def listen(self):
        with self.mic as source:
            print("Listening...")
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Add a small pause after speaking and before listening
            time.sleep(1)
            
            try:
                print("Recording...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Processing audio...")
                
                try:
                    response = self.recognizer.recognize_google(audio)
                    print(f"Heard: {response}")  # Debug print
                    return response.lower()
                except sr.UnknownValueError:
                    print("Could not understand audio")
                    self.speak("Sorry, I couldn't understand that. Please try again.")
                    return None
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    self.speak("Sorry, there was an error with the speech recognition service.")
                    return None
                    
            except sr.WaitTimeoutError:
                print("Timeout waiting for phrase")
                self.speak("Sorry, I didn't hear anything. Please try again.")
                return None
                
    def get_questions(self, category=None, difficulty=None):
        # Start with questions from voice quizzes only
        query = Question.objects.filter(quiz__quiz_type='voice')
        
        if category:
            query = query.filter(quiz__subject=category)
        if difficulty:
            query = query.filter(difficulty=difficulty)
        
        questions = list(query.order_by('?')[:5])  # Get 5 random questions
        
        if questions:
            self.current_quiz = questions[0].quiz
        
        return questions
        
    def run_quiz(self, category=None, difficulty=None):
        self.speak(f"Welcome {self.user.username} to the Voice Quiz!")
        questions = self.get_questions(category, difficulty)
        self.total_questions = len(questions)
        
        # Store the quiz object for later use
        self.current_quiz = questions[0].quiz if questions else None
        
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
                user_answer = self.listen()
                
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
                        'answer 4': 4, '4': 4
                    }
                    
                    # Clean up the answer and convert to lowercase
                    user_answer = user_answer.strip().lower()
                    
                    # Debug prints
                    print(f"Recognized answer: {user_answer}")
                    print(f"Correct answer from database: {question.correct_answer}")
                    print(f"Type of correct answer: {type(question.correct_answer)}")
                    
                    # Try to map the answer to a number
                    mapped_answer = answer_map.get(user_answer)
                    print(f"Mapped to: {mapped_answer}")
                    print(f"Type of mapped answer: {type(mapped_answer)}")
                    
                    if mapped_answer is not None:
                        answer_received = True
                        # Convert both to integers for comparison
                        if int(mapped_answer) == int(question.correct_answer):
                            print("Comparison result: True")  # Debug print
                            self.speak("Correct answer!")
                            self.score += 1
                        else:
                            print("Comparison result: False")  # Debug print
                            self.speak(f"Wrong answer! The correct answer was option {question.correct_answer}")
                    else:
                        self.speak("Please say a number between 1 and 4")
                
                attempts += 1
                
            if not answer_received:
                self.speak("Moving to the next question")
        
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

    def listen_for_answer(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("Listening for your answer...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                answer = self.recognizer.recognize_google(audio)
                return answer.lower()
            except sr.WaitTimeoutError:
                return "No answer received"
            except sr.UnknownValueError:
                return "Could not understand audio"
            except sr.RequestError:
                return "Could not request results"

    def check_answer(self, user_answer, correct_answer):
        return user_answer.lower() == correct_answer.lower()

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