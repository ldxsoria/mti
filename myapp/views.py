from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import  AuthenticationForm #SIGNIN

#PROJECTS ROUTES
from django.contrib.auth import login, logout, authenticate #para crear cookie de inicio de sesion
from django.contrib.auth.decorators import login_required #MAIN

# Create your views here.
def signin(request):
    #Si esta autenticado la pagina principal debe de ser main
    if request.user.is_authenticated:
        return render(request, 'main.html')
    else:
        if request.method == 'GET':
            return render(request, 'signin.html',{
            'form': AuthenticationForm
        })
        else:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

            if user is None:
                return render(request, 'signin.html',{
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
            else:
                login(request, user)
                return redirect('main/')

#@login_required
def main(request):
    return render(request, 'main.html')
