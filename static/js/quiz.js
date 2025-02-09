let startTime;
let timerInterval;

function startTimer() {
    startTime = Date.now();
    const timerDisplay = document.querySelector('#timer span');
    
    timerInterval = setInterval(() => {
        const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
        const minutes = Math.floor(elapsedTime / 60);
        const seconds = elapsedTime % 60;
        timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }, 1000);
}

// Handle option selection
function initializeOptionButtons() {
    console.log('Initializing option buttons'); // Debug log
    const buttons = document.querySelectorAll('.option-btn');
    console.log('Found buttons:', buttons.length); // Debug log
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            console.log('Button clicked'); // Debug log
            // Remove selected class from other options in the same question
            const questionCard = this.closest('.question-card');
            questionCard.querySelectorAll('.option-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            // Add selected class to clicked button
            this.classList.add('selected');
        });
    });
}

// Handle form submission
function initializeQuizForm(submitUrl, quizId, csrfToken, redirectUrl) {
    const quizForm = document.getElementById('quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            e.preventDefault();
            clearInterval(timerInterval);

            const answers = {};
            document.querySelectorAll('.option-btn.selected').forEach(button => {
                const questionId = button.dataset.question;
                const selectedText = button.textContent.trim();
                answers[questionId] = selectedText;
            });

            if (Object.keys(answers).length === 0) {
                alert('Please select at least one answer before submitting.');
                return;
            }

            fetch(submitUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    quiz_id: quizId,
                    answers: answers
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(`Quiz completed!\nScore: ${data.score}%\nCorrect Answers: ${data.correct_answers}/${data.total_questions}`);
                window.location.href = redirectUrl;
            })
            .catch(error => {
                console.error('Error submitting quiz:', error);
                alert('There was an error submitting your quiz. Please try again.');
            });
        });
    }
}

// Initialize quiz functionality
function initializeQuiz(hasCurrentQuiz) {
    console.log('Initializing quiz:', hasCurrentQuiz); // Debug log
    if (hasCurrentQuiz) {
        // Add a small delay to ensure DOM is ready
        setTimeout(() => {
            initializeOptionButtons();
            startTimer();
        }, 100);
    }
}

// Make sure event listeners are added when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded'); // Debug log
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Button clicked directly'); // Debug log
            const questionCard = this.closest('.question-card');
            questionCard.querySelectorAll('.option-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            this.classList.add('selected');
        });
    });
}); 