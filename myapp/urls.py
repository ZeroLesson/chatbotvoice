from django.urls import path
from myapp import views
urlpatterns = [
    path('',views.index,name="/"),
    path('api',views.api,name="api"),
    
]