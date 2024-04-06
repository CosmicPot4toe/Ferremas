from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages as msgs
from .form import *

# Create your views here.
def test(req):
	return render(req,'clienteView.html')

def login(req):
	return render(req,'accounts/login.html')

def signup(req):
	form = RegUserForm()

	if req.POST:
		form = RegUserForm(req.POST)
		if form.is_valid():
			form.save()
			name =form.cleaned_data.get('username')
			msgs.success(req,'cuenta creada para '+ name)

			return redirect('login')
	ctx={'form':form}
	return render(req,'accounts/signup.html',ctx)