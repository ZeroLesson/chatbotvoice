from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import os
import requests
# Create your views here.
def login(request):
    if request.method == "POST":
        # ตรวจสอบว่ามีข้อมูลใน request.POST หรือไม่
        if "email" in request.POST and "password" in request.POST:
            email = request.POST["email"]
            password = request.POST["password"]
            api_url = "http://localhost:5217/api/Users/login"
            headers = {
                "email": email,
                "password": password
            }
            try:
                response = requests.post(api_url, json=headers)

                if response.status_code == 200:
                    result = response.json()
                    token = result.get("token")
                    if token:
                        request.session['token'] = token
                        return redirect("chat")
                else:
                    messages.error(request, "Invalid email or password")
                    return redirect("login")
            except requests.exceptions.RequestException as e:
                messages.error(request, f"Error occurred: {str(e)}")
                return redirect("login")
        else:
            return redirect("login")
    else:
        return render(request, "login.html")
    
def logout(request):
    # ลบข้อมูลทั้งหมดใน session
    request.session.flush()  # หรือลบแค่ token: request.session.pop('token', None)
    return redirect("login") 

def register(request):
    return render(request, "register.html")

def chat(request):
    api_url="http://localhost:5217/api/Users"
    token = request.session.get('token')
    print(token)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return render(request, "chat.html")

def record_audio_view(request):
    return render(request, 'record.html')

@csrf_exempt  # ปิด CSRF protection สำหรับการทดสอบ (ไม่แนะนำใน production)
def upload_audio_view(request):
    if request.method == 'POST':
        audio_file = request.FILES['audio']
        with open(os.path.join('media', audio_file.name), 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)
        return JsonResponse({'message': 'Audio uploaded successfully!'})
    return JsonResponse({'error': 'Invalid request'}, status=400)