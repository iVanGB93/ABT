from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import AccountSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


from user.models import RegistrationCode
import threading

from user.models import Profile

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, queryset=None, **kwargs):
        data = request.data
        response = {'OK': False}
        action = data['action']
        email = data['email']
        if action == 'email':
            if User.objects.filter(email=email).exists():
                response['message'] = "This email is already taken."
                return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, data=response)
            else:
                if RegistrationCode.objects.filter(email=email).exists():
                    new_code = RegistrationCode.objects.get(email=email)
                else:
                    new_code = RegistrationCode(email=email)
                    new_code.save()
                
                # Send professional registration code email
                try:
                    current_site = get_current_site(request)
                    
                    # Create email context
                    context = {
                        'code': new_code.code,
                        'email': email,
                        'site_name': 'ABT - Advance Business Tools',
                    }
                    
                    # Render email template
                    email_subject = 'Your ABT Registration Code - Complete Your Account'
                    email_body = render_to_string('user/email_registration_code.html', context)
                    
                    # Send registration code email
                    send_mail(
                        email_subject,
                        f'Your ABT registration code is: {new_code.code}',  # Fallback text
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                        html_message=email_body
                    )
                except Exception as e:
                    print(f"Registration code email failed to send: {e}")
                    # Still return success to not break the flow, but log the error
                
                response['message'] = "A verification code was sent to your email, please check it and continue."
                response['code'] = new_code.code
                response['email'] = new_code.email
                return Response(status=status.HTTP_200_OK, data=response)
        username = data['username']
        password = data['password']
        if User.objects.filter(username=username).exists():
            response['message'] = "Username is already taken."
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, data=response)
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.save()
        code = RegistrationCode.objects.get(email=email)
        code.user = new_user
        code.used = timezone.now()
        code.active = False
        code.save()
        
        # Send welcome email using the professional template
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
            print(f"Welcome email failed to send: {e}")
        
        response['OK'] = True
        response['message'] = "Account created."
        return Response(status=status.HTTP_201_CREATED, data=response)

class AccountView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        user = self.kwargs.get('pk')
        user = User.objects.get(username=user)
        profile = Profile.objects.get(user=user)
        data = AccountSerializer(profile).data
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        data = request.data
        print(data)
        user = self.kwargs.get('pk')
        user = User.objects.get(username=user)
        profile = Profile.objects.get(user=user)
        
        # Track changes for email notification
        changes = {}
        old_values = {
            'email': user.email,
            'phone': profile.phone,
            'address': profile.address,
        }
        
        # Update fields and track changes
        new_phone = data.get('phone', profile.phone)
        new_address = data.get('address', profile.address)
        new_email = data.get('email', user.email)
        
        if old_values['phone'] != new_phone:
            changes['phone'] = True
            profile.phone = new_phone
            
        if old_values['address'] != new_address:
            changes['address'] = True
            profile.address = new_address
            
        if old_values['email'] != new_email:
            changes['email'] = True
            user.email = new_email
        
        # Handle image update
        if 'image' in data and data.get('image'):
            changes['image'] = True
            profile.image = data.get('image')
        
        user.save()
        profile.save()
        
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
                print(f"Profile update notification email failed to send: {e}")
        
        data = AccountSerializer(profile).data
        return Response(status=status.HTTP_200_OK, data=data)
    
class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request, queryset=None, **kwargs):
        email = request.data.get('email')
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
            return Response(status=status.HTTP_200_OK, data=content)

        except User.DoesNotExist:
            content = {'message': 'No account exists with that email.', 'type': 'error'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=content)

