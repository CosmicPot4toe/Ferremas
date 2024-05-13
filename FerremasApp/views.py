from django.http import HttpRequest
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages as msgs
from .form import *
from .models import User


# Create your views here.

#@login_required(login_url='login')
def userView(req: HttpRequest ):
	#ctx={'t':req.user.get_type_display().split(' ',1)[0]}
	ctx={'t':'lul'}
	return render(req, 'app/index.html',ctx)
	# match req.user.type:
	# 	case 'Bod':
	# 		return render(req, 'bodegueroView.html',ctx)
	# 	case 'Ven':
	# 		return render(req, 'vendedorView.html',ctx)
	# 	case 'Con':
	# 		return render(req, 'contadorView.html',ctx)
	# 	case 'Cli':
	# 		return render(req, 'app/index.html',ctx)
	# 	case _:
	# 		return render(req, 'app/index.html',ctx)


def logoutP(req: HttpRequest):
	logout(req)
	return redirect('login')

def loginP(req: HttpRequest):
		if req.method == 'POST':
				usern_or_email = req.POST.get('username_or_email')
				passw = req.POST.get('password')

				if usern_or_email is not None and passw is not None:
						# Buscar si el usuario existe con el nombre de usuario o correo electrónico
						user = None
						if '@' in usern_or_email:
								try:
										user = User.objects.get(email=usern_or_email)
								except User.DoesNotExist:
										pass
						else:
								user = authenticate(req, username=usern_or_email, password=passw)

						if user is not None:
								login(req, user)
								return redirect('index')
						else:
								msgs.info(req, 'Nombre de usuario, correo electrónico o contraseña incorrectos')
				else:
						msgs.info(req, 'Nombre de usuario o contraseña no proporcionados')
						
		return render(req, 'registration/login.html')

def signup(req: HttpRequest):
	form = RegUserForm()
	if req.POST:
		form = RegUserForm(req.POST)
		if form.is_valid():
			form.save()
			name =form.cleaned_data.get('username')
			msgs.success(req,'cuenta creada para '+ name)
			return redirect('login')
	ctx={'form':form}
	return render(req,'registration/signup.html',ctx)