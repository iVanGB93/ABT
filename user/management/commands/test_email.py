from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
import logging
import threading
import time

logger = logging.getLogger(__name__)

class AsyncEmailTest(threading.Thread):
    """Test email sending in background thread"""
    def __init__(self, email_subject, email_body, email_html, recipient_email, test_type):
        threading.Thread.__init__(self)
        self.email_subject = email_subject
        self.email_body = email_body  
        self.email_html = email_html
        self.recipient_email = recipient_email
        self.test_type = test_type
        self.daemon = True
        self.result = None
        
    def run(self):
        try:
            start_time = time.time()
            send_mail(
                self.email_subject,
                self.email_body,
                settings.DEFAULT_FROM_EMAIL,
                [self.recipient_email],
                fail_silently=False,
                html_message=self.email_html
            )
            end_time = time.time()
            self.result = f"SUCCESS: {self.test_type} email sent in {end_time - start_time:.2f} seconds"
        except Exception as e:
            self.result = f"ERROR: {self.test_type} email failed - {str(e)}"

class Command(BaseCommand):
    help = 'Test email configuration and send a test email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test email to')
        parser.add_argument('--type', type=str, default='simple', 
                          choices=['simple', 'welcome', 'reset', 'async', 'provider'],
                          help='Type of test email to send')
        parser.add_argument('--async', action='store_true', 
                          help='Test asynchronous email sending')
        parser.add_argument('--provider', type=str, 
                          choices=['gmail', 'sendgrid', 'mailgun'],
                          help='Test specific email provider')

    def handle(self, *args, **options):
        email = options.get('email')
        if not email:
            self.stdout.write(self.style.ERROR('Please provide an email address with --email'))
            return

        email_type = options['type']
        use_async = options['async'] or email_type == 'async'
        test_provider = options.get('provider')

        try:
            self.stdout.write(f'Testing email configuration...')
            self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
            self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
            self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
            self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
            self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
            
            # Show current provider
            if 'sendgrid' in settings.EMAIL_HOST:
                self.stdout.write(self.style.SUCCESS('📧 Current Provider: SendGrid'))
            elif 'mailgun' in settings.EMAIL_HOST:
                self.stdout.write(self.style.SUCCESS('📧 Current Provider: Mailgun'))
            elif 'gmail' in settings.EMAIL_HOST:
                self.stdout.write(self.style.WARNING('📧 Current Provider: Gmail (may fail on Railway)'))
            
            if use_async:
                self.stdout.write(self.style.WARNING('Testing ASYNCHRONOUS email sending...'))

            if email_type == 'provider':
                # Test provider connectivity
                self.stdout.write(f'🔌 Testing {settings.EMAIL_HOST} connectivity...')
                import socket
                try:
                    socket.create_connection((settings.EMAIL_HOST, settings.EMAIL_PORT), timeout=10)
                    self.stdout.write(self.style.SUCCESS(f'✅ Connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT} successful'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Connection failed: {str(e)}'))
                    if 'gmail.com' in settings.EMAIL_HOST:
                        self.stdout.write(self.style.WARNING('💡 Railway often blocks Gmail. Try SendGrid or Mailgun.'))
                    return

            if email_type == 'simple' or email_type == 'async':
                # Send simple test email
                if use_async:
                    email_thread = AsyncEmailTest(
                        'ABT Email Test (Async)',
                        'This is an ASYNCHRONOUS test email from ABT. If you received this, async email is working!',
                        None,
                        email,
                        'Simple Async'
                    )
                    email_thread.start()
                    self.stdout.write('Async email thread started... waiting for completion...')
                    email_thread.join(timeout=30)  # Wait max 30 seconds
                    if email_thread.result:
                        if "SUCCESS" in email_thread.result:
                            self.stdout.write(self.style.SUCCESS(email_thread.result))
                        else:
                            self.stdout.write(self.style.ERROR(email_thread.result))
                    else:
                        self.stdout.write(self.style.WARNING('Async email thread timed out'))
                else:
                    send_mail(
                        'ABT Email Test',
                        'This is a test email from ABT. If you received this, email configuration is working!',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    self.stdout.write(self.style.SUCCESS(f'Simple test email sent successfully to {email}'))

            elif email_type == 'welcome':
                # Send welcome email template
                context = {
                    'user': {'username': 'testuser', 'email': email, 'first_name': 'Test'},
                    'login_url': 'http://example.com/login/',
                    'site_name': 'ABT - Advance Business Tools',
                    'registration_date': '2025-09-03',
                }
                
                email_body_html = render_to_string('user/email_welcome.html', context)
                email_body_text = render_to_string('user/email_welcome.txt', context)
                
                send_mail(
                    'Welcome to ABT - Test Email',
                    email_body_text,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    html_message=email_body_html
                )
                self.stdout.write(self.style.SUCCESS(f'Welcome email template sent successfully to {email}'))

            elif email_type == 'reset':
                # Send password reset email template
                context = {
                    'user': {'username': 'testuser', 'email': email, 'first_name': 'Test'},
                    'reset_url': 'http://example.com/reset/test123/token456/',
                    'site_name': 'ABT - Advance Business Tools',
                }
                
                email_body = render_to_string('user/email_reset_password.html', context)
                
                send_mail(
                    'Password Reset Test - ABT',
                    'Test password reset email',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                    html_message=email_body
                )
                self.stdout.write(self.style.SUCCESS(f'Password reset email template sent successfully to {email}'))

        except Exception as e:
            logger.error(f"Email test failed: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Email test failed: {str(e)}'))
            self.stdout.write(self.style.ERROR('Check your email configuration and try again.'))
