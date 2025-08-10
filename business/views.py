from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Business, ExtraIncome, ExtraExpense, Invitation
from job.models import Job
from client.models import Client


@login_required
def business_list(request):
    business_list = Business.objects.filter(owners=request.user).order_by('name')
    context = { 'business_list': business_list }
    return render(request, 'business/business-list.html', context)

@login_required
def add_income(request, pk):
    business = get_object_or_404(Business, pk=pk)
    
    # Verificar que el usuario sea propietario del negocio
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to manage this business.')
        return redirect('business:business_detail', pk=pk)
    
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
            
        return redirect('business:business_detail', pk=pk)
    
    context = {
        'business': business,
    }
    return render(request, 'business/add-income.html', context)

@login_required
def add_expense(request, pk):
    business = get_object_or_404(Business, pk=pk)
    
    # Verificar que el usuario sea propietario del negocio
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to manage this business.')
        return redirect('business:business_detail', pk=pk)
    
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
            
        return redirect('business:business_detail', pk=pk)
    
    # Obtener las opciones de categorías desde el modelo
    category_choices = ExtraExpense.CATEGORY_CHOICES
    
    context = {
        'business': business,
        'category_choices': category_choices,
    }
    return render(request, 'business/add-expense.html', context)

@login_required
def financial_report(request, pk):
    business = get_object_or_404(Business, pk=pk)
    
    # Verificar que el usuario sea propietario del negocio
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to view this business.')
        return redirect('business:business_detail', pk=pk)
    
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
def business_edit(request, pk):
    business = get_object_or_404(Business, pk=pk)
    
    # Verificar permisos
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to edit this business.')
        return redirect('business:business_detail', pk=pk)
    
    if request.method == 'POST':
        business.name = request.POST.get('name', business.name)
        business.description = request.POST.get('description', business.description)
        business.address = request.POST.get('address', business.address)
        business.save()
        
        messages.success(request, 'Business updated successfully!')
        return redirect('business:business_detail', pk=pk)
    
    context = {
        'business': business,
    }
    return render(request, 'business/business-edit.html', context)

@login_required
def business_delete(request, pk):
    business = get_object_or_404(Business, pk=pk)
    
    # Verificar permisos
    if request.user not in business.owners.all():
        messages.error(request, 'You do not have permission to delete this business.')
        return redirect('business:business_detail', pk=pk)
    
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
            return redirect('business:business_detail', pk=business.id)
        else:
            messages.error(request, 'Business name is required.')
    
    return render(request, 'business/business-create.html')

@login_required
def business_detail(request, pk):
    business = get_object_or_404(Business, pk=pk)
    
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
    completed_jobs = Job.objects.filter(business=business, status='finished')
    for job in completed_jobs:
        job_income += float(job.price)  # CONVERTIR A FLOAT AQUÍ
    
    total_jobs = Job.objects.filter(business=business).count()
    completed_jobs_count = Job.objects.filter(business=business, status='finished').count()
    pending_jobs_count = Job.objects.filter(business=business, status='new').count()
    in_progress_jobs_count = Job.objects.filter(business=business, status='active').count()
    
    # Ahora todas las variables son float, no habrá problemas de tipo
    total_income = extra_income + job_income
    net_profit = total_income - total_expenses
    
    # Transacciones recientes
    recent_incomes = business.extra_income.order_by('-date')[:3]
    recent_jobs = completed_jobs.order_by('-date')[:3] if completed_jobs else []
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
            status='finished',  # Cambié 'completed' por 'finished' para consistencia
            date__gte=month_start,
            date__lte=month_end
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
    }
    
    return render(request, 'business/business-detail.html', context)

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