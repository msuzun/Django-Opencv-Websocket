# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('<str:room_name>/', views.room, name='room'),
    path("", views.index, name="anasayfa" ),
    # path("detail",views.detail, name="detail"),
    # path('video_stream', views.video_stream, name='video_stream'),
    path('lessondetail', views.lessondetail, name="lessondetail"),
]