from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChatRoom(models.Model):
	roomname=models.CharField(max_length=30,unique=True)
	roomid=models.CharField(max_length=12,unique=True)
	
	def __str__(self):
		return self.roomname
