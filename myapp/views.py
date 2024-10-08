from django.shortcuts import render,redirect
from django.http import HttpResponse
import requests
# Create your views here.
def index(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        print(email , password)
        if email == "banyawat.t@ku.th" and password == "Ban@071145":
            return redirect('api')
        else:
            return redirect('/')
    else:
        return render(request, "index.html")

def api(request):
    api_url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(api_url)
    if response.status_code == 200:
            # ดึงข้อมูล JSON จาก API
        data = response.json()
    else:
        data = {'error': 'Failed to retrieve data'}

    # ส่งข้อมูลไปยังเทมเพลต หรือแสดงผลเป็น JSON
    return render(request, 'api.html', {'data': data})