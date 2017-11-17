from django.shortcuts import render,render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext
from django import forms
from django.contrib.auth.models import User
import logging

# Create your views here.


class userRegisterForm(forms.Form):
	username=forms.CharField(max_length=32)
	email=forms.EmailField(required=False)
	password1=forms.CharField(max_length=32,widget=forms.PasswordInput())
	password2=forms.CharField(max_length=32,widget=forms.PasswordInput())
	
def register(request):
	#if request.user.is_authenticated():
	#	return HttpResponseRedirect('/homepage')
	errors=[]
	try:
		if request.method=='POST':
			username=request.POST.get('username','')
			email=request.POST.get('email','')
			password1=request.POST.get('password1','')
			password2=request.POST.get('password2','')
			
		
		registerForm=userRegisterForm({'username':username,'email':email,'password1':password1,'password2':password2})
		if not registerForm.is_valid():
			errors.extend(registerForm.errors.values())
			return render(request,'user/register.html',{'username':username,'email':email,'errors':errors})
		password1=registerForm.cleaned_data['password1']
		password2=registerForm.cleaned_data['password2']
		username=registerForm.cleaned_data['username']
		email=registerForm.cleaned_data['email']
		if password1!=password2:
			errors.append("Two passwords don't match!Try again.")
			return render(request,'user/register.html',{'username':username,'email':email,'errors':errors})
		try:
			User.objects.get(username=username)
		except User.DoesNotExist:
			pass
		else:
			errors.append('User name already exist!Try a new one.')
			return render(request,'user/register.html',{'username':username,'email':email,'errors':errors})
		newUser=User.objects.create_user(username=username,email=email,password=password1)
		newUser.set_password(password1)
		newUser.save()
		loginUser=auth.authenticate(username=username,password=password1)
		if loginUser is not None:
			auth.login(request,loginUser)
			return HttpResponseRedirect('/homepage')
	except Exception as e:
		errors.append(str(e))
		return render(request,'user/register.html',{'username':'error'})

def login(request):
	context={'loginStatus':''}
	if request.method=='POST':
		username=request.POST.get('username')
		password=request.POST.get('password')
		loginUser=auth.authenticate(username=username,password=password)
		if loginUser is not None:
			auth.login(request,loginUser)
			return HttpResponseRedirect('/homepage')
		context['loginStatus']=u'Invalid username of password'
	return render(request,'user/login.html',context)

@login_required(login_url='/accounts/login')
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/accounts/login')