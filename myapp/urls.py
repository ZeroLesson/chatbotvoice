from django.urls import path
from myapp import views

urlpatterns = [
    path('',views.index),
    path('register',views.register),
    path('chat', views.chat)
]