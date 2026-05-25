from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Business, ExtraIncome, ExtraExpense, Invitation
from job.models import Job
from client.models import Client
from item.models import Item_List
from schedule.models import Schedule


@login_required
def business_list(request):
    business_list = Business.objects.filter(owners=request.user).order_by('name')
    context = { 'business_list': business_list }
    return render(request, 'business/business-list.html', context)

@login_required
def add_income(request, business_name):
    business = get_object_or_404(Business, name=business_name)
    
    # Verificar que el usuario sea propietario del negocio
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to manage this business.')
        return redirect('business:business_detail', business_name=business.name)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        
        if description and amount:
            try:
                ExtraIncome.objects.create(
                    business=business,
                    description=description,
                    amount=float(amount)
                )
                messages.success(request, f'Income of ${amount} added successfully!')
            except ValueError:
                messages.error(request, 'Invalid amount format.')
        else:
            messages.error(request, 'Please fill in all required fields.')
            
        return redirect('business:business_detail', business_name=business.name)
    
    context = {
        'business': business,
    }
    return render(request, 'business/add-income.html', context)

@login_required
def add_expense(request, business_name):
    business = get_object_or_404(Business, name=business_name)
    
    # Verificar que el usuario sea propietario del negocio
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to manage this business.')
        return redirect('business:business_detail', business_name=business.name)
    
    if request.method == 'POST':
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        is_tax_deductible = request.POST.get('is_tax_deductible') == 'on'
        
        if description and amount and category:
            try:
                ExtraExpense.objects.create(
                    business=business,
                    description=description,
                    amount=float(amount),
                    category=category,
                    tax_deductible=is_tax_deductible
                )
                messages.success(request, f'Expense of ${amount} added successfully!')
            except ValueError:
                messages.error(request, 'Invalid amount format.')
        else:
            messages.error(request, 'Please fill in all required fields.')
            
        return redirect('business:business_detail', business_name=business.name)
    
    # Obtener las opciones de categorías desde el modelo
    category_choices = ExtraExpense.CATEGORY_CHOICES
    
    context = {
        'business': business,
        'category_choices': category_choices,
    }
    return render(request, 'business/add-expense.html', context)

@login_required
def financial_report(request, business_name):
    business = get_object_or_404(Business, name=business_name)
    
    # Verificar que el usuario sea propietario del negocio
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to view this business.')
        return redirect('business:business_detail', business_name=business.name)
    
    # Obtener parámetros de filtro
    period = request.GET.get('period', 'month')
    
    # Calcular fechas según el período
    now = timezone.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'quarter':
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = now - timedelta(days=30)
    
    # Obtener datos financieros filtrados
    incomes = business.extra_income.filter(date__gte=start_date)
    expenses = business.extra_expenses.filter(date__gte=start_date)
    
    # Calcular totales - convertir a float
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = float(total_income)
    
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = float(total_expenses)
    
    net_profit = total_income - total_expenses
    
    # Gastos por categoría - ARREGLAR ESTO
    expense_categories = {}
    for expense in expenses:
        category = expense.get_category_display()
        current_amount = expense_categories.get(category, 0.0)
        expense_categories[category] = current_amount + float(expense.amount)
    
    # Preparar datos para JSON - NUEVO
    expense_categories_labels = list(expense_categories.keys())
    expense_categories_data = list(expense_categories.values())
    
    # Gastos deducibles de impuestos
    tax_deductible_expenses = expenses.filter(tax_deductible=True)  # Cambié is_tax_deductible por tax_deductible
    total_tax_deductible = tax_deductible_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_tax_deductible = float(total_tax_deductible)
    
    context = {
        'business': business,
        'period': period,
        'start_date': start_date,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'incomes': incomes.order_by('-date'),
        'expenses': expenses.order_by('-date'),
        'expense_categories': expense_categories,  # Para mostrar en template
        'expense_categories_labels': json.dumps(expense_categories_labels),  # Para Chart.js
        'expense_categories_data': json.dumps(expense_categories_data),      # Para Chart.js
        'total_tax_deductible': total_tax_deductible,
        'tax_deductible_expenses': tax_deductible_expenses,
    }
    
    return render(request, 'business/financial-report.html', context)

@login_required
def business_edit(request, business_name):
    business = get_object_or_404(Business, name=business_name)
    
    # Verificar permisos
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to edit this business.')
        return redirect('business:business_detail', business_name=business.name)
    
    if request.method == 'POST':
        business.name = request.POST.get('name', business.name)
        business.description = request.POST.get('description', business.description)
        business.address = request.POST.get('address', business.address)
        business.save()
        
        messages.success(request, 'Business updated successfully!')
        return redirect('business:business_detail', business_name=business.name)
    
    context = {
        'business': business,
    }
    return render(request, 'business/business-edit.html', context)

@login_required
def business_delete(request, business_name):
    business = get_object_or_404(Business, name=business_name)
    
    # Verificar permisos
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to delete this business.')
        return redirect('business:business_detail', business_name=business.name)
    
    if request.method == 'POST':
        business_name = business.name
        business.delete()
        messages.success(request, f'Business "{business_name}" deleted successfully!')
        return redirect('business:business_list')
    
    context = {
        'business': business,
    }
    return render(request, 'business/business-delete.html', context)

@login_required
def create_business(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        address = request.POST.get('address')
        
        if name:
            business = Business.objects.create(
                name=name,
                description=description,
                address=address
            )
            business.owners.add(request.user)
            
            messages.success(request, f'Business "{name}" created successfully!')
            return redirect('business:business_detail', business_name=business.name)
        else:
            messages.error(request, 'Business name is required.')
    
    return render(request, 'business/business-create.html')

@login_required
def business_detail(request, business_name):
    business = get_object_or_404(Business, name=business_name)

    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to view this business.')
        return redirect('business:business_list')
    
    # Calcular métricas financieras básicas - CONVERTIR A FLOAT INMEDIATAMENTE
    extra_income_raw = business.extra_income.aggregate(Sum('amount'))['amount__sum'] or 0
    extra_income = float(extra_income_raw)  # Convertir a float inmediatamente
    
    total_expenses_raw = business.extra_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = float(total_expenses_raw)  # Convertir a float inmediatamente
    
    # Calcular ingresos de trabajos si el modelo existe
    job_income = 0.0  # Inicializar como float
    completed_jobs = []
    total_jobs = 0
    completed_jobs_count = 0
    pending_jobs_count = 0
    in_progress_jobs_count = 0
    completed_jobs = Job.objects.filter(business=business, status='completed')
    for job in completed_jobs:
        job_income += float(job.price)  # CONVERTIR A FLOAT AQUÍ
    
    total_jobs = Job.objects.filter(business=business).count()
    completed_jobs_count = Job.objects.filter(business=business, status='completed').count()
    pending_jobs_count = Job.objects.filter(business=business, status='pending').count()
    in_progress_jobs_count = Job.objects.filter(business=business, status='in_progress').count()
    
    # Ahora todas las variables son float, no habrá problemas de tipo
    total_income = extra_income + job_income
    net_profit = total_income - total_expenses
    
    # Transacciones recientes
    recent_incomes = business.extra_income.order_by('-date')[:3]
    recent_jobs = completed_jobs.order_by('-created_at')[:3] if completed_jobs else []
    recent_expenses = business.extra_expenses.order_by('-date')[:5]
    
    # Datos para gráficos (últimos 6 meses)
    monthly_income = []
    monthly_expenses = []
    monthly_job_income = []
    
    now = timezone.now()
    today = now.date()
    
    for i in range(6):
        # Calcular fechas del mes
        if today.month - i <= 0:
            year = today.year - 1
            month = 12 + (today.month - i)
        else:
            year = today.year
            month = today.month - i
            
        # Crear datetime con zona horaria
        month_start = timezone.datetime(year, month, 1)
        if month == 12:
            month_end = timezone.datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = timezone.datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Asegurar que tienen zona horaria
        month_start = timezone.make_aware(month_start) if timezone.is_naive(month_start) else month_start
        month_end = timezone.make_aware(month_end) if timezone.is_naive(month_end) else month_end
        
        # Ingresos extra del mes - CONVERTIR A FLOAT
        month_extra_income_raw = business.extra_income.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        month_extra_income = float(month_extra_income_raw)
        
        # Ingresos de trabajos del mes
        month_job_income = 0.0
        month_jobs = Job.objects.filter(
            business=business,
            status='completed',  # Usar el status correcto del modelo
            created_at__gte=month_start,
            created_at__lte=month_end
        )
        for job in month_jobs:
            month_job_income += float(job.price)  # CONVERTIR A FLOAT
        # Gastos del mes - CONVERTIR A FLOAT
        month_expenses_raw = business.extra_expenses.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        month_expenses = float(month_expenses_raw)
        
        # Todas las operaciones ahora son float + float
        monthly_income.append(month_extra_income + month_job_income)
        monthly_job_income.append(month_job_income)
        monthly_expenses.append(month_expenses)
    
    # Revertir para orden cronológico
    monthly_income.reverse()
    monthly_job_income.reverse()
    monthly_expenses.reverse()
    
    # Gastos por categoría - CONVERTIR A FLOAT
    expense_categories_data = {}
    for expense in business.extra_expenses.all():
        category = expense.get_category_display()
        current_amount = expense_categories_data.get(category, 0.0)
        expense_categories_data[category] = current_amount + float(expense.amount)
    
    # Estadísticas de clientes
    total_clients = 0
    active_clients = 0
    total_clients = Client.objects.filter(business=business).count()
    active_clients = total_clients

    recent_clients = Client.objects.filter(business=business).order_by('-created_at')[:5]

    total_items = Item_List.objects.filter(business=business).count()
    low_stock_items_count = Item_List.objects.filter(business=business, amount__lte=3).count()
    recent_items = Item_List.objects.filter(business=business).order_by('-date')[:5]

    job_content_type = ContentType.objects.get_for_model(Job)
    business_job_ids = Job.objects.filter(business=business).values_list('id', flat=True)
    schedules = Schedule.objects.filter(
        content_type=job_content_type,
        object_id__in=business_job_ids,
    )
    total_schedules = schedules.count()
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    today_schedules_count = schedules.filter(start_at__lt=today_end, end_at__gte=today_start).count()
    upcoming_schedules = schedules.filter(start_at__gte=timezone.now(), is_cancelled=False).order_by('start_at')[:5]
    
    context = {
        'business': business,
        'total_income': total_income,
        'extra_income': extra_income,
        'job_income': job_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'current_balance': net_profit,
        'recent_incomes': recent_incomes,
        'recent_jobs': recent_jobs,
        'recent_expenses': recent_expenses,
        'monthly_income': json.dumps(monthly_income),
        'monthly_job_income': json.dumps(monthly_job_income),
        'monthly_expenses': json.dumps(monthly_expenses),
        'expense_categories_labels': json.dumps(list(expense_categories_data.keys())),
        'expense_categories_data': json.dumps(list(expense_categories_data.values())),
        # Estadísticas adicionales
        'total_jobs': total_jobs,
        'completed_jobs_count': completed_jobs_count,
        'pending_jobs_count': pending_jobs_count,
        'in_progress_jobs_count': in_progress_jobs_count,
        'total_clients': total_clients,
        'active_clients': active_clients,
        'recent_clients': recent_clients,
        'total_items': total_items,
        'low_stock_items_count': low_stock_items_count,
        'recent_items': recent_items,
        'total_schedules': total_schedules,
        'today_schedules_count': today_schedules_count,
        'upcoming_schedules': upcoming_schedules,
    }
    
    return render(request, 'business/business-detail.html', context)


@login_required
def business_schedule(request, business_name):
    business = get_object_or_404(Business, name=business_name)

    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to view this business schedule.')
        return redirect('business:business_list')

    job_content_type = ContentType.objects.get_for_model(Job)
    business_job_ids = Job.objects.filter(business=business).values_list('id', flat=True)

    schedules = Schedule.objects.filter(
        content_type=job_content_type,
        object_id__in=business_job_ids,
    ).order_by('start_at')

    jobs_by_id = {
        job.id: job
        for job in Job.objects.filter(id__in=business_job_ids).select_related('client')
    }

    schedule_events = []
    for event in schedules:
        linked_job = jobs_by_id.get(event.object_id)
        title = event.title
        if not title and linked_job:
            title = linked_job.description
        schedule_events.append(
            {
                'id': event.id,
                'title': title,
                'start': event.start_at,
                'end': event.end_at,
                'location': event.location,
                'is_cancelled': event.is_cancelled,
                'job_id': linked_job.id if linked_job else None,
                'job_status': linked_job.status if linked_job else '',
                'client_name': f'{linked_job.client.name} {linked_job.client.last_name}' if linked_job else '',
            }
        )

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    pending_jobs = Job.objects.filter(
        business=business,
    ).exclude(
        status__in=['completed', 'cancelled', 'paid']
    ).select_related('client').order_by('-created_at')

    pending_jobs_json = json.dumps([
        {
            'id': j.id,
            'description': j.description,
            'client_name': f'{j.client.name} {j.client.last_name}',
            'status': j.status,
            'status_display': j.get_status_display(),
            'price': str(j.price),
        }
        for j in pending_jobs
    ])

    context = {
        'business': business,
        'schedules': schedules,
        'today_schedules': schedules.filter(start_at__lt=today_end, end_at__gte=today_start),
        'upcoming_schedules': schedules.filter(start_at__gte=now, is_cancelled=False)[:10],
        'past_schedules': schedules.filter(end_at__lt=now)[:10],
        'total_schedules': schedules.count(),
        'today_schedules_count': schedules.filter(start_at__lt=today_end, end_at__gte=today_start).count(),
        'schedule_events_json': json.dumps(schedule_events, cls=DjangoJSONEncoder),
        'pending_jobs_json': pending_jobs_json,
        'job_content_type_id': job_content_type.id,
    }

    return render(request, 'business/business-schedule.html', context)


@login_required
def business_clients(request, business_name):
    business = get_object_or_404(Business, name=business_name)

    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to view this business clients.')
        return redirect('business:business_list')

    clients = Client.objects.filter(business=business).order_by('-created_at')

    context = {
        'business': business,
        'clients': clients,
        'total_clients': clients.count(),
        'clients_with_email': clients.exclude(email='no@email.saved').count(),
    }

    return render(request, 'business/business-clients.html', context)


@login_required
def create_business_client(request, business_name):
    business = get_object_or_404(Business, name=business_name)
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission.')
        return redirect('business:business_list')

    if request.method == 'POST':
        client = Client(
            business=business,
            provider=request.user,
            name=request.POST.get('name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', 'no@email.saved'),
            phone=request.POST.get('phone', 'no phone saved'),
            address=request.POST.get('address', 'no address saved'),
        )
        if request.FILES.get('image'):
            client.image = request.FILES['image']
        client.save()
        messages.success(request, 'Client created successfully.')
        return redirect('business:business_clients', business_name=business_name)

    return render(request, 'business/business-create-client.html', {'business': business})


@login_required
def business_client_detail(request, business_name, client_id):
    business = get_object_or_404(Business, name=business_name)
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission.')
        return redirect('business:business_list')

    client = get_object_or_404(Client, id=client_id, business=business)
    jobs = client.jobs.order_by('-created_at')

    context = {
        'business': business,
        'client': client,
        'jobs': jobs,
    }
    return render(request, 'business/business-client-detail.html', context)


@login_required
def business_items(request, business_name):
    business = get_object_or_404(Business, name=business_name)

    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to view this business items.')
        return redirect('business:business_list')

    items = Item_List.objects.filter(business=business).order_by('-date')

    context = {
        'business': business,
        'items': items,
        'total_items': items.count(),
        'low_stock_items_count': items.filter(amount__lte=3).count(),
        'inventory_value': sum(float(item.price) * int(item.amount) for item in items),
    }

    return render(request, 'business/business-items.html', context)

@login_required(login_url='/user/login/')
def business_invitation(request, code):
    try:
        invitation = Invitation.objects.get(code=code)
        invited_email = invitation.email.lower().strip()
        user_email = request.user.email.lower().strip()
        is_invited_user = invited_email == user_email
        if request.method == 'POST':
            business = invitation.business
            user = request.user
            if is_invited_user:
                business.owners.add(user)
                business.save()
                return render(request, 'business/business-invitation-accepted.html', {'business': business})
            else:
                return render(request, 'business/business-invitation-invalid.html', {'message': 'This invitation is not for you or you are not logged in with the correct account.'})
        return render(request, 'business/business-invitation.html', {'invitation': invitation, 'is_invited_user': is_invited_user})
    except Invitation.DoesNotExist:
        return render(request, 'business/business-invitation-invalid.html', {'code': code})
    
@login_required(login_url='/user/login/')
def business_invitation_form(request):
    code = request.POST.get('code')
    try:
        invitation = Invitation.objects.get(code=code)
        invited_email = invitation.email.lower().strip()
        user_email = request.user.email.lower().strip()
        is_invited_user = invited_email == user_email
        if not is_invited_user:
            return render(request, 'business/business-invitation-invalid.html', {'message': 'This invitation is not for you or you are not logged in with the correct account.'})
        business = invitation.business
        user = request.user
        business.owners.add(user)
        business.save()
        return render(request, 'business/business-invitation-accepted.html', {'business': business})
    except Invitation.DoesNotExist:
        return render(request, 'business/business-invitation-invalid.html', {'code': code})