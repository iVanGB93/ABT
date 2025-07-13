from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Business, Invitation


def business_list(request):
    business_list = Business.objects.filter(owners=request.user).order_by('name')
    context = { 'business_list': business_list }
    return render(request, 'business/business-list.html', context)

def business_detail(request, business_id):
    business = Business.objects.get(id=business_id)
    context = { 'business': business }
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