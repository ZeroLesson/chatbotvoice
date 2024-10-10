from django.urls import path
from myapp import views

urlpatterns = [
    path('',views.login,name="login"),
    path('register',views.register,name="register"),
    path('chat', views.chat,name="chat"),
    path('record/', views.record_audio_view, name='record-audio'),
    path('upload-audio/', views.upload_audio_view, name='upload-audio'),
    path('logout/', views.logout, name='logout'),
    path('add_conversation/', views.add_conversation, name='add_conversation'),
]