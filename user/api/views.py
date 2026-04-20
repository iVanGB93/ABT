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
import logging

# Configure logger for email debugging
logger = logging.getLogger(__name__)


from user.models import RegistrationCode
import threading

from user.models import Profile

class EmailSendingThread(threading.Thread):
    """Thread class for sending emails asynchronously"""
    def __init__(self, email_subject, email_body_text, email_body_html, recipient_email):
        threading.Thread.__init__(self)
        self.email_subject = email_subject
        self.email_body_text = email_body_text
        self.email_body_html = email_body_html
        self.recipient_email = recipient_email
        self.daemon = True  # Die when main thread dies
        
    def run(self):
        try:
            send_mail(
                self.email_subject,
                self.email_body_text,
                settings.DEFAULT_FROM_EMAIL,
                [self.recipient_email],
                fail_silently=False,
                html_message=self.email_body_html
            )
            logger.info(f"Email sent successfully to {self.recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {self.recipient_email}: {str(e)}")

class PasswordResetEmailThread(threading.Thread):
    """Thread class for sending password reset emails asynchronously"""
    def __init__(self, email_subject, email_body, recipient_email):
        threading.Thread.__init__(self)
        self.email_subject = email_subject
        self.email_body = email_body
        self.recipient_email = recipient_email
        self.daemon = True
        
    def run(self):
        try:
            send_mail(
                self.email_subject,
                self.email_body,
                settings.DEFAULT_FROM_EMAIL,
                [self.recipient_email],
                fail_silently=False,
                html_message=self.email_body
            )
            logger.info(f"Password reset email sent successfully to {self.recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {self.recipient_email}: {str(e)}")

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
                
                # Send professional registration code email asynchronously
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
                    email_body_html = render_to_string('user/email_registration_code.html', context)
                    email_body_text = f'Your ABT registration code is: {new_code.code}'
                    
                    # Send email asynchronously
                    email_thread = EmailSendingThread(
                        email_subject, 
                        email_body_text, 
                        email_body_html, 
                        email
                    )
                    email_thread.start()
                    
                except Exception as e:
                    logger.error(f"Failed to start email thread for {email}: {str(e)}")
                    # Continue anyway, don't break the registration flow
                
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
        
        # Send welcome email using the professional template asynchronously
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
            
            # Send welcome email asynchronously
            email_thread = EmailSendingThread(
                email_subject,
                email_body_text,
                email_body_html,
                new_user.email
            )
            email_thread.start()
            
        except Exception as e:
            # Log the error but don't break the registration process
            logger.error(f"Failed to start welcome email thread for {new_user.email}: {str(e)}")
            logger.error(f"Welcome email failed to send: {e}")
        
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
        logger.debug('AccountView POST data: %s', data)
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
                email_body_html = render_to_string('user/email_profile_updated.html', context)
                email_body_text = f'Your ABT profile was updated. If this wasn\'t you, please contact support.'
                
                # Send notification email asynchronously
                email_thread = EmailSendingThread(
                    email_subject,
                    email_body_text,
                    email_body_html,
                    user.email
                )
                email_thread.start()
                
            except Exception as e:
                # Log the error but don't break the profile update process
                logger.error(f"Failed to start profile update email thread: {str(e)}")
                logger.error(f"Profile update notification email failed to send: {e}")
        
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
            
            # Send email asynchronously
            email_thread = PasswordResetEmailThread(
                email_subject,
                email_body,
                user.email
            )
            email_thread.start()
            
            content = {'message': 'A password reset link has been sent to your email.', 'type': 'success'}
            return Response(status=status.HTTP_200_OK, data=content)

        except User.DoesNotExist:
            content = {'message': 'No account exists with that email.', 'type': 'error'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=content)
        except Exception as e:
            logger.error(f"Password reset email failed to send: {str(e)}")
            content = {'message': 'An error occurred while sending the reset email. Please try again.', 'type': 'error'}
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=content)

