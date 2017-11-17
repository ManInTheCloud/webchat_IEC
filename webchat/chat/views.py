from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login
from chat.models import ChatRoom
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import json

# Create your views here.

@login_required(login_url='/accounts/login')
def index(request):
	user=request.user
	RoomObj=ChatRoom.objects.all()
	return render_to_response('chat/index.html',{'user':user,'RoomObj':RoomObj})
	
@login_required(login_url='/accounts/login')
def room(request,roomid):
	user=request.user
	roomObj=ChatRoom.objects.get(id=roomid)
	return render_to_response("chat/room.html", {'user': str(user), 'roomObj': roomObj})

