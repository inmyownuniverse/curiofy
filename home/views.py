from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
import json
import google.generativeai as genai


def index_view(request):
    return render(request, 'home/index.html')

def home_view(request):
    return render(request, 'home/home.html')

def explore_view(request):
    return render(request, 'home/explore.html')

def about_view(request):
    return render(request, 'home/about.html')

def community_view(request):
    return render(request, 'home/community.html')

def get_gemini_key(request):
    if request.user.is_authenticated:
        return JsonResponse({'key': settings.GEMINI_API_KEY})
    return JsonResponse({'error': 'User not authenticated'}, status=401)

@csrf_protect
def translate_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            target_language = data.get('target_language')

            # Configure Gemini
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')

            # Create the prompt
            prompt = f"Translate this text to {target_language}: {text}"
            
            # Get response from Gemini
            response = model.generate_content(prompt)
            
            return JsonResponse({
                'translated_text': response.text,
                'success': True
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'success': False
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)