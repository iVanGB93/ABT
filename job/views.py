from django.shortcuts import render, redirect
from .models import Job, Spent
from .forms import JobForm, SpentForm
from django.contrib.auth.models import User
from user.models import Profile


def soon(request):
    return render(request, 'job/soon.html')

def client_list(request):
    clients = Profile.objects.filter(is_client=True)
    content = {'clients': clients}
    return render(request, 'job/client-list.html', content)

def create_client(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email', 'example@email.com')
        new_user = User(username=username, email=email)
        new_user.first_name = username
        new_user.set_password('temporaryPassword')
        new_user.save()
        profile = Profile.objects.get(user=new_user)
        profile.phone = request.POST.get('phone', '-')
        profile.address = request.POST.get('address', '-')
        if request.FILES.get('image'):
            profile.image = request.FILES['image']
        profile.save()
        return redirect('job:client_list')
    return render(request, 'job/create-client.html')

def client_detail(request, id):
    client = Profile.objects.get(id=id)
    content = {'client': client}
    return render(request, 'job/client-detail.html', content)

def job_list(request):
    jobs = Job.objects.all()
    content = {'jobs': jobs}
    return render(request, 'job/job-list.html', content)

def create_job(request):
    form = JobForm
    content = {'form': form}
    if request.method == 'POST':
        copydata = request.POST.copy()
        profile = Profile.objects.get(id=request.POST['client'])
        if request.POST.get('sameAddress'):
            if profile.address != None:
                copydata['address'] = profile.address
            else:
                content['message': 'El cliente no tiene direccion guardada']
                return render(request, 'job/create-job.html', content)
        form = JobForm(copydata, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('job:job_list')
        else:
            content['message'] = form.errors
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