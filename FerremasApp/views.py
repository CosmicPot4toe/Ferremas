from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages as msgs
from .form import *
from .models import User


# Create your views here.

#restrinje que el ususario este iniciado
@login_required(login_url='login')
def test(req):
    if req.user.type == 'Bod':
        #print(req.user[])
        return render(req, 'bodegueroView.html')
    elif req.user.type == 'Ven':
        return render(req, 'vendedorView.html')
    elif req.user.type == 'Con':
        return render(req, 'contadorView.html')
    else:
        return render(req, 'clienteView.html')

def logoutP(req):
	logout(req)
	return redirect('login')

def loginP(req):
    if req.method == 'POST':
        usern = req.POST.get('username')
        passw = req.POST.get('password')
        user = authenticate(req, username=usern, password=passw)
        if user is not None:
            login(req, user)
            return redirect('client')  # Llama a la vista 'test' en lugar de 'client'
        else:
            msgs.info(req, 'Nombre de usuario o contraseña incorrectos')
    return render(req, 'accounts/login.html')

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