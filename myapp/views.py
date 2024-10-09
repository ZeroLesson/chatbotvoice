from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import os
import requests
# Create your views here.
def index(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        api_url = "http://localhost:5217/api/Users/login"
        headers = {
            "email": email,
            "password": password
        }
        try:
            # ส่ง POST request ไปที่ API
            response = requests.post(api_url, json=headers)

            # ตรวจสอบสถานะการตอบกลับ
            if response.status_code == 200:
                result = response.json()
                token = result.get("token")
                if token:
                    # เก็บ token ลงใน session
                    request.session['token'] = token
                    return redirect("chat")
            else:
                messages.error(request, "Invalid email or password")
                return redirect("login")
        except requests.exceptions.RequestException as e:
            # จัดการข้อผิดพลาดที่เกิดจากการเชื่อมต่อ เช่น API ล่ม หรือเชื่อมต่อไม่ได้
            return JsonResponse({"error": f"Error occurred: {str(e)}"}, status=500)
    else:
        return render(request, "login.html")

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