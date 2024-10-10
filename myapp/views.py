from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import os
import requests
import json

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
                    id = result.get("userId")
                    if token:
                        request.session['token'] = token
                        request.session['userId'] = id
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
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")
        
        # API URL ที่ต้องการเรียกใช้งาน
        api_url = "http://localhost:5217/api/Users/register"
        
        # ข้อมูลที่ส่งไปยัง API
        data = {
            "email": email,
            "password": password,
            "username": username
        }
        
        try:
            # ส่ง POST request ไปที่ API
            response = requests.post(api_url, json=data)

            # ตรวจสอบสถานะการตอบกลับ
            if response.status_code == 200:
                # ส่งข้อความ success
                messages.success(request, response.text)
                return render(request, "register.html", {"registration_success": True})
            else:
                # กรณีเกิดข้อผิดพลาด และแสดงข้อความจาก API
                messages.error(request, f"Failed to register: {response.text}")
                return render(request, "register.html")
        except requests.exceptions.RequestException as e:
            # จัดการข้อผิดพลาดที่เกิดจากการเชื่อมต่อ เช่น API ล่ม หรือเชื่อมต่อไม่ได้
            messages.error(request, f"Error occurred: {str(e)}")
            return render(request, "register.html")
    
    return render(request, "register.html")

def chat(request):
    token = request.session.get('token')
    user_id = request.session.get('userId')  # เปลี่ยนชื่อจาก id เป็น user_id เพื่อให้ชัดเจนขึ้น

    # ตรวจสอบว่ามี token หรือไม่
    if not token:
        messages.error(request, "Please login!!")
        return redirect("login")

    # สร้าง API URL สำหรับดึงข้อมูลการสนทนา
    api_url1 = f"http://localhost:5217/api/Conversation/user/{user_id}"
    api_url2 = "http://localhost:5217/api/Users"
    headers = {
        "Authorization": f"Bearer {token}"  # เพิ่ม Bearer token ใน header
    }
    try:
        response1 = requests.get(api_url1,headers=headers)  # ส่งคำขอ GET
        response2 = requests.get(api_url2,headers=headers)
        # ตรวจสอบสถานะการตอบกลับ
        if response1.status_code == 200:
            result1 = response1.json()
            result2 = response2.json()
            result2 = [item for item in result2 if item['id'] != user_id]
            for r1_item in result1:
                if r1_item['user_2']['id'] == user_id:
                    result2 = [item for item in result2 if item['id'] != r1_item['user_1']['id']]
                else:
                    result2 = [item for item in result2 if item['id'] != r1_item['user_2']['id']]
            return render(request, "chat.html", {"data": result1, "user":result2,"user_id":user_id})  # ส่งข้อมูลไปยัง template
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error occurred: {str(e)}")  # แจ้งข้อผิดพลาด
        return redirect("login")  # หรือ redirect ไปยังหน้า login หากเกิดข้อผิดพลาด
    
@csrf_exempt 
def add_conversation(request):
    if request.method == "POST":
        token = request.session.get('token')
        user_id1 = request.session.get('userId')
        data = json.loads(request.body)
        user_id2 = data.get('user_id')
        headers = {
        "Authorization": f"Bearer {token}"  # เพิ่ม Bearer token ใน header
        }
        api_url = f"http://localhost:5217/api/Conversation/create?user_1={user_id1}&user_2={user_id2}"
        try:
            response = requests.post(api_url,headers=headers)  # ส่งคำขอ GET
        # ตรวจสอบสถานะการตอบกลับ
            if response.status_code == 200:
                return redirect("chat")
            else:
                messages.error(request, "Failed to retrieve conversations.")  # แจ้งข้อผิดพลาด
                return redirect("chat")
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error occurred: {str(e)}")  # แจ้งข้อผิ
            return redirect("chat")
    
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