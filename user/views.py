from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('web:index')
            else:
                content = {'message': 'contraseña incorrecta'}
                return render(request, 'user/login.html', content)
        content = {'message': 'usuario no existe'}
        return render(request, 'user/login.html', content)            
    return render(request, 'user/login.html')

def logoutView(request):
    logout(request)
    return redirect('web:index')