from django.shortcuts import render, redirect
from .models import Job, Spent
from .forms import JobForm, SpentForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def job_list(request):
    jobs = Job.objects.all()
    content = {'jobs': jobs}
    return render(request, 'job/job-list.html', content)

def create_job(request):
    form = JobForm
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            error = form.errors
            print(error)
        return redirect('job:job_list')
    content = {'form': form}
    return render(request, 'job/create-job.html', content)

def job_detail(request, id):
    job = Job.objects.get(id=id)
    spents = Spent.objects.filter(job=job)
    total_spent = 0
    for spent in spents:
        total_spent = total_spent + spent.amount
    profit = job.price - total_spent
    content = {'job': job, 'spents': spents, 'total_spent': total_spent, 'profit': profit}
    return render(request, 'job/job-detail.html', content)

def delete_job(request, id):
    job = Job.objects.get(id=id)
    job.delete()
    jobs = Job.objects.all()
    content = {'jobs': jobs}
    return render(request, 'job/job-list.html', content)

def create_spent(request, id):
    job = Job.objects.get(id=id)
    form = SpentForm
    if request.method == 'POST':
        form = SpentForm(request.POST, request.FILES)
        if form.is_valid():
            job_form = form.save(commit=False)
            job_form.job_id = job.id
            job_form.save()
        else:
            error = form.errors
            print("ERROR", error)
        job.status = 'active'
        job.save()
        return redirect('job:job_detail', job.id)
    content = {'form': form, 'job': job}
    return render(request, 'job/create-spent.html', content)

def spent_detail(request, id):
    spent = Spent.objects.get(id=id)
    content = {'spent': spent}
    return render(request, 'job/spent-detail.html', content)

def close_job(request, id):
    job = Job.objects.get(id=id)
    job.closed = True
    job.status = 'finished'
    job.save()
    return redirect('job:job_list')

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
                return render(request, 'job/login.html', content)
        content = {'message': 'usuario no existe'}
        return render(request, 'job/login.html', content)            
    return render(request, 'job/login.html')