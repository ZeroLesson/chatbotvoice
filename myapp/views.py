from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http import StreamingHttpResponse, JsonResponse
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
        token = request.session.get('token')
        headers = {
            "Authorization": f"Bearer {token}"  # เพิ่ม Bearer token ใน header
        }

        # ตรวจสอบการส่งข้อมูล ID มาพร้อมกันใน request
        conid = request.session.get('conid')
        id1 = request.session.get('id1')
        id2 = request.session.get('id2')

        if 'audio' in request.FILES:  # ตรวจสอบว่ามีไฟล์ audio ถูกส่งมาหรือไม่
            audio_file = request.FILES['audio']
            file_path = os.path.join('media', audio_file.name)

            # ตรวจสอบโฟลเดอร์ media ว่ามีอยู่หรือไม่ ถ้าไม่มีให้สร้างขึ้นมา
            if not os.path.exists('media'):
                os.makedirs('media')

            try:
                # บันทึกไฟล์เสียงลงในระบบไฟล์ของคุณ
                with open(file_path, 'wb+') as destination:
                    for chunk in audio_file.chunks():
                        destination.write(chunk)

                # ตรวจสอบว่าไฟล์ถูกบันทึกเรียบร้อย
                if not os.path.exists(file_path):
                    return JsonResponse({'error': 'File not saved correctly'}, status=500)

                # เตรียมข้อมูลที่จะส่งไปยัง API อื่น
                api_url = 'http://localhost:5217/api/Messages/create/'

                # ข้อมูล data ที่ต้องการส่งไปพร้อมไฟล์
                data = {
                    "conversation_id": conid,  # รับค่าจาก POST request
                    "sender_id": id1,  # รับค่าจาก POST request
                    "receiver_id": id2,  # รับค่าจาก POST request
                }

                # เตรียมไฟล์เสียงสำหรับการส่ง
                files = {'audioFile': (audio_file.name, open(file_path, 'rb'), audio_file.content_type)}

                # ส่งไฟล์เสียงพร้อมกับข้อมูลไปยัง API อื่นด้วย requests
                response = requests.post(api_url, data=data, files=files, headers=headers)

                # ตรวจสอบผลลัพธ์จาก API อื่น
                if response.status_code == 200:
                    return JsonResponse({'message': 'Audio uploaded successfully and sent to API!'})
                else:
                    return JsonResponse({'error': f'Failed to send audio to API: {response.text}'}, status=response.status_code)

            except Exception as e:
                return JsonResponse({'error': f'Error occurred while processing the file: {str(e)}'}, status=500)

        else:
            return JsonResponse({'error': 'No audio file provided'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt 
def test_view(request):
    if request.method == "POST":
        token = request.session.get('token')
        headers = {
            "Authorization": f"Bearer {token}"  # เพิ่ม Bearer token ใน header
        }
        data = json.loads(request.body)
        con_id = data.get('con_id')
        id_1 = data.get('id_1')
        id_2 = data.get('id_2')
        request.session['conid'] = con_id
        request.session['id1'] = id_1
        request.session['id2'] = id_2
        
        # ดึงข้อมูลจาก API
        api_url = f'http://localhost:5217/api/Messages/get-all-by-conversation-id/{con_id}'
        api_url2 = "http://localhost:5217/api/Users"
        response = requests.get(api_url, headers=headers)
        response2 = requests.get(api_url2,headers=headers)
        
        try:
            api_data = response.json()  # พยายามแปลง response เป็น JSON
            user_data = response2.json()
            data = {
                'status': 'success',
                'message': 'Data processed successfully!',
                'apidata': api_data,
                'userdata': user_data,
            }
            return JsonResponse(data)
        except ValueError:
            # ถ้าแปลง JSON ไม่สำเร็จ
            return JsonResponse({'error': 'Failed to parse JSON from API response', 'raw_response': response.text}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_decrypted_audio(request):
    if request.method == 'POST':
        try:
            token = request.session.get('token')
            headers = {
                "Authorization": f"Bearer {token}"  # เพิ่ม Bearer token ใน header
            }
            data = json.loads(request.body)
            voice_path = data.get('voice_path')
            print(f"Received voice_path: {voice_path}")  # ดูว่าได้รับ voice_path มาหรือไม่
            
            if not voice_path:
                return JsonResponse({'error': 'No voice_path provided'}, status=400)
            
            api_url = f'http://localhost:5217/api/Messages/get-audio?voice_path={voice_path}'
            
            print(f"Requesting decrypted audio for: {voice_path}")
            response = requests.get(api_url, stream=True, headers=headers)
            
            if response.status_code == 200:
                print(f"Successfully received audio for {voice_path}")
                http_response = StreamingHttpResponse(
                    streaming_content=(chunk for chunk in response.iter_content(chunk_size=8192)),
                    content_type='audio/m4a'
                )
                http_response['Content-Disposition'] = f'inline; filename="{voice_path}.m4a"'
                return http_response
            else:
                error_message = f"Failed to retrieve file from API: {response.text}"
                print(error_message)
                return JsonResponse({'error': error_message}, status=response.status_code)

        except Exception as e:
            error_message = f"An error occurred while processing the request: {str(e)}"
            print(error_message)
            return JsonResponse({'error': error_message}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

