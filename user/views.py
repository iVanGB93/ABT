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
                next_url = request.GET.get('next', 'web:index')
                return redirect(next_url)
            else:
                content = {'message': 'contraseña incorrecta'}
                return render(request, 'user/login.html', content)
        content = {'message': 'usuario no existe'}
        return render(request, 'user/login.html', content)            
    return render(request, 'user/login.html')

def registerView(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            content = {'message': 'User already exists'}
            return render(request, 'user/register.html', content)
        if User.objects.filter(email=email).exists():
            content = {'message': 'Email already registered'}
            return render(request, 'user/register.html', content)
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.save()
        login(request, new_user)
        return redirect('web:index')
    return render(request, 'user/register.html')

def logoutView(request):
    logout(request)
    return redirect('web:index')