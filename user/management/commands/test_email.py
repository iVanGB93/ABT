from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test email configuration and send a test email'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address to send test email to')
        parser.add_argument('--type', type=str, default='simple', 
                          choices=['simple', 'welcome', 'reset'],
                          help='Type of test email to send')

    def handle(self, *args, **options):
        email = options.get('email')
        if not email:
            self.stdout.write(self.style.ERROR('Please provide an email address with --email'))
            return

        email_type = options['type']

        try:
            self.stdout.write(f'Testing email configuration...')
            self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
            self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
            self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
            self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
            self.stdout.write(f'DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')

            if email_type == 'simple':
                # Send simple test email
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
