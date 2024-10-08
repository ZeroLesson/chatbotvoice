from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from datetime import datetime

# Create your views here.
def index(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        print(email , password)
        if email == "banyawat.t@ku.th" and password == "Ban@071145":
            return redirect('chat')
        else:
            return redirect('login')
    else:
        return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def chat(request):
    return render(request, "chat.html")

def record_audio_view(request):
    return render(request, 'record.html')

@csrf_exempt  # ปิด CSRF protection สำหรับการทดสอบ (ไม่แนะนำใน production)
def upload_audio_view(request):
    if request.method == 'POST':
        audio_file = request.FILES['audio']
        now = datetime.now()
        with open(os.path.join('media', audio_file.name), 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        return JsonResponse({'message': 'Audio uploaded successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)