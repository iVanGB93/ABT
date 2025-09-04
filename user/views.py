from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import logging

# Configure logger for email debugging
logger = logging.getLogger(__name__)
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

def loginView(request):
    if request.user.is_authenticated:
        return redirect('web:index')
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
    if request.user.is_authenticated:
        return redirect('web:index')
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
        
        # Send welcome email
        try:
            current_site = get_current_site(request)
            login_url = f"http://{current_site.domain}/user/login/"
            
            # Create email context
            context = {
                'user': new_user,
                'login_url': login_url,
                'site_name': 'ABT - Advance Business Tools',
                'registration_date': new_user.date_joined,
            }
            
            # Render email templates
            email_subject = 'Welcome to ABT - Your account is ready!'
            email_body_html = render_to_string('user/email_welcome.html', context)
            email_body_text = render_to_string('user/email_welcome.txt', context)
            
            # Send welcome email with both HTML and text versions
            send_mail(
                email_subject,
                email_body_text,  # Plain text version as main body
                settings.DEFAULT_FROM_EMAIL,
                [new_user.email],
                fail_silently=True,  # Don't break registration if email fails
                html_message=email_body_html  # HTML version as alternative
            )
        except Exception as e:
            # Log the error but don't break the registration process
            logger.error(f"Welcome email failed to send to {new_user.email}: {str(e)}")
            print(f"Welcome email failed to send: {e}")
        
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
        
        # Track changes
        changes = {}
        old_values = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        
        # Update fields
        new_first_name = request.POST.get('first_name', user.first_name)
        new_last_name = request.POST.get('last_name', user.last_name)
        new_email = request.POST.get('email', user.email)
        
        # Check for changes
        if old_values['first_name'] != new_first_name:
            changes['first_name'] = True
            user.first_name = new_first_name
            
        if old_values['last_name'] != new_last_name:
            changes['last_name'] = True
            user.last_name = new_last_name
            
        if old_values['email'] != new_email:
            changes['email'] = True
            user.email = new_email
        
        user.save()
        
        # Send notification email if there were changes
        if changes:
            try:
                current_site = get_current_site(request)
                
                # Create email context
                context = {
                    'user': user,
                    'changes': changes,
                    'site_name': 'ABT - Advance Business Tools',
                    'update_date': timezone.now(),
                }
                
                # Render email template
                email_subject = 'ABT Profile Updated - Security Notification'
                email_body = render_to_string('user/email_profile_updated.html', context)
                
                # Send notification email
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=True,  # Don't break profile update if email fails
                    html_message=email_body
                )
            except Exception as e:
                # Log the error but don't break the profile update process
                logger.error(f"Profile update notification email failed to send: {str(e)}")
                print(f"Profile update notification email failed to send: {e}")
        
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

def forgotPasswordView(request):
    if request.user.is_authenticated:
        return redirect('web:index')
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate token and uid
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            current_site = get_current_site(request)
            reset_url = f"http://{current_site.domain}/user/reset-password/{uid}/{token}/"
            
            # Create email context
            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'ABT - Advance Business Tools',
            }
            
            # Render email template
            email_subject = 'Reset your password on ABT'
            email_body = render_to_string('user/email_reset_password.html', context)
            
            # Send email
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=email_body
            )
            
            content = {'message': 'A password reset link has been sent to your email.', 'type': 'success'}
            return render(request, 'user/forgot-password.html', content)
            
        except User.DoesNotExist:
            content = {'message': 'No account exists with that email.', 'type': 'error'}
            return render(request, 'user/forgot-password.html', content)
        except Exception as e:
            logger.error(f"Password reset email failed to send: {str(e)}")
            content = {'message': 'An error occurred while sending the reset email. Please try again.', 'type': 'error'}
            return render(request, 'user/forgot-password.html', content)
    
    return render(request, 'user/forgot-password.html')

def resetPasswordView(request, uidb64, token):
    if request.user.is_authenticated:
        return redirect('web:index')
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                if new_password == confirm_password:
                    if len(new_password) < 6:
                        content = {'message': 'Password must be at least 6 characters long.', 'type': 'error', 'valid_link': True}
                        return render(request, 'user/reset-password.html', content)
                    else:
                        user.set_password(new_password)
                        user.save()
                        content = {'message': 'Your password has been reset successfully.', 'type': 'success'}
                        return render(request, 'user/reset-success.html', content)
                else:
                    content = {'message': 'Passwords do not match.', 'type': 'error', 'valid_link': True}
                    return render(request, 'user/reset-password.html', content)
            
            return render(request, 'user/reset-password.html', {'valid_link': True})
        else:
            content = {'message': 'The reset link is invalid or has expired.', 'type': 'error', 'valid_link': False}
            return render(request, 'user/reset-password.html', content)
    
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        content = {'message': 'The reset link is invalid.', 'type': 'error', 'valid_link': False}
        return render(request, 'user/reset-password.html', content)