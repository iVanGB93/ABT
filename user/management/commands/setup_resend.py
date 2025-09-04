from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from decouple import config
import requests
import json

class Command(BaseCommand):
    help = 'Test and validate Resend configuration'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Testing Resend Email Configuration...")
        self.stdout.write("-" * 50)
        
        # Check configuration
        resend_api_key = config('RESEND_API_KEY', default='NOT_SET')
        resend_from = config('RESEND_FROM_EMAIL', default='NOT_SET')
        
        self.stdout.write(f"📧 From Email: {resend_from}")
        self.stdout.write(f"🔑 API Key: {'✅ Set' if resend_api_key != 'NOT_SET' else '❌ Not Set'}")
        
        if resend_api_key == 'NOT_SET' or resend_api_key == 'AQUI_PONER_RESEND_API_KEY':
            self.stdout.write(self.style.ERROR("❌ Resend API Key not configured!"))
            self.stdout.write("\n📝 Steps to configure Resend:")
            self.stdout.write("1. Go to https://resend.com")
            self.stdout.write("2. Sign up (no credit card required)")
            self.stdout.write("3. Go to API Keys section")
            self.stdout.write("4. Create new API key")
            self.stdout.write("5. Update settings.ini: RESEND_API_KEY=re_xxxxxxxxx")
            return
        
        # Test API connection
        self.stdout.write("\n🔌 Testing Resend API connection...")
        try:
            headers = {
                'Authorization': f'Bearer {resend_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Test with Resend API (not SMTP)
            test_data = {
                'from': resend_from,
                'to': ['test@example.com'],  # This won't actually send
                'subject': 'Test from ABT System',
                'html': '<p>This is a test email from ABT system using Resend!</p>'
            }
            
            # Don't actually send, just validate credentials
            response = requests.get('https://api.resend.com/domains', headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS("✅ Resend API connection successful!"))
                domains = response.json().get('data', [])
                if domains:
                    self.stdout.write(f"📍 Available domains: {[d.get('name') for d in domains]}")
                else:
                    self.stdout.write("📍 No custom domains configured (using resend default)")
            else:
                self.stdout.write(self.style.ERROR(f"❌ API Error: {response.status_code}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Connection failed: {str(e)}"))
        
        # Test Django email
        self.stdout.write("\n📧 Testing Django email with Resend...")
        try:
            # Use Django's send_mail with SMTP
            result = send_mail(
                subject='Test Email from ABT',
                message='This is a test email from ABT system.',
                from_email=resend_from,
                recipient_list=[config('EMAIL_ALERTS', default='test@example.com')],
                fail_silently=False,
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS("✅ Email sent successfully!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Email failed to send"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Email error: {str(e)}"))
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📋 Resend Configuration Summary:")
        self.stdout.write(f"   Provider: {config('EMAIL_PROVIDER', default='gmail')}")
        self.stdout.write(f"   From: {resend_from}")
        self.stdout.write(f"   SMTP Host: smtp.resend.com:587")
        self.stdout.write("   Free Tier: 100 emails/day, 3000/month")
        self.stdout.write("   Documentation: https://resend.com/docs")
