# chat/views.py
from django.shortcuts import render


# Create your views here.
def index(request):
   
    return render(request,"video_stream/index.html")

def room(request,room_name):
   return render(request, 'video_stream/room.html', {
        'room_name': room_name
    })
# def detail(request):
    
#     return render(request,"video_stream/detail.html")

def lessondetail(request):

    return render(request, "video_stream/lessondetail.html")

