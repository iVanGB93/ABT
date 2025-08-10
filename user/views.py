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

def profileView(request):
    return render(request, 'user/profile.html')

def editProfileView(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        return redirect('user:profile')
    return render(request, 'user/edit-profile.html')

def changePasswordView(request):
    if request.method == 'POST':
        user = request.user
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return redirect('user:profile')
        else:
            content = {'message': 'Current password is incorrect'}
            return render(request, 'user/change-password.html', content)
    return render(request, 'user/change-password.html')