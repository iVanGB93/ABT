from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Configure SendGrid for Railway deployment'

    def add_arguments(self, parser):
        parser.add_argument('--test', action='store_true', help='Test SendGrid connectivity')
        parser.add_argument('--setup', action='store_true', help='Show setup instructions')

    def handle(self, *args, **options):
        if options['setup']:
            self.show_setup_instructions()
        elif options['test']:
            self.test_sendgrid()
        else:
            self.show_current_config()

    def show_current_config(self):
        self.stdout.write(self.style.SUCCESS('📧 Current Email Configuration\n'))
        
        self.stdout.write(f'EMAIL_HOST: {getattr(settings, "EMAIL_HOST", "Not set")}')
        self.stdout.write(f'EMAIL_PORT: {getattr(settings, "EMAIL_PORT", "Not set")}')
        self.stdout.write(f'EMAIL_HOST_USER: {getattr(settings, "EMAIL_HOST_USER", "Not set")}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL: {getattr(settings, "DEFAULT_FROM_EMAIL", "Not set")}')
        
        if hasattr(settings, 'EMAIL_HOST') and 'sendgrid' in settings.EMAIL_HOST:
            self.stdout.write(self.style.SUCCESS('\n✅ SendGrid is configured!'))
        elif hasattr(settings, 'EMAIL_HOST') and 'gmail.com' in settings.EMAIL_HOST:
            self.stdout.write(self.style.WARNING('\n⚠️  Gmail is configured (may fail on Railway)'))
            self.stdout.write('Consider switching to SendGrid for Railway deployment.')
        else:
            self.stdout.write(self.style.ERROR('\n❌ Email provider not recognized'))

    def show_setup_instructions(self):
        self.stdout.write(self.style.SUCCESS('🚀 SendGrid Setup Instructions for Railway\n'))
        
        self.stdout.write('1. Create SendGrid Account:')
        self.stdout.write('   • Go to https://sendgrid.com/')
        self.stdout.write('   • Sign up for free account (100 emails/day)')
        self.stdout.write('   • Verify your email address\n')
        
        self.stdout.write('2. Create API Key:')
        self.stdout.write('   • Go to Settings > API Keys')
        self.stdout.write('   • Click "Create API Key"')
        self.stdout.write('   • Choose "Restricted Access"')
        self.stdout.write('   • Enable "Mail Send" permission')
        self.stdout.write('   • Copy the API key (save it safely!)\n')
        
        self.stdout.write('3. Set Railway Environment Variables:')
        self.stdout.write(self.style.WARNING('   EMAIL_PROVIDER=sendgrid'))
        self.stdout.write(self.style.WARNING('   SENDGRID_API_KEY=your_api_key_here'))
        self.stdout.write(self.style.WARNING('   SENDGRID_FROM_EMAIL=noreply@abt.qbared.com\n'))
        
        self.stdout.write('4. Optional - Verify Sender Identity:')
        self.stdout.write('   • Go to Settings > Sender Authentication')
        self.stdout.write('   • Add Single Sender Verification')
        self.stdout.write('   • Use: noreply@abt.qbared.com')
        self.stdout.write('   • Verify the email address\n')
        
        self.stdout.write('5. Test Configuration:')
        self.stdout.write(self.style.SUCCESS('   python manage.py setup_sendgrid --test\n'))
        
        self.stdout.write('💡 Benefits of SendGrid:')
        self.stdout.write('   ✅ Works perfectly with Railway')
        self.stdout.write('   ✅ Better deliverability than Gmail')
        self.stdout.write('   ✅ Professional email service')
        self.stdout.write('   ✅ Free tier: 100 emails/day')
        self.stdout.write('   ✅ Advanced analytics and tracking')

    def test_sendgrid(self):
        self.stdout.write(self.style.SUCCESS('🧪 Testing SendGrid Configuration\n'))
        
        if not hasattr(settings, 'EMAIL_HOST') or 'sendgrid' not in settings.EMAIL_HOST:
            self.stdout.write(self.style.ERROR('❌ SendGrid not configured'))
            self.stdout.write('Run: python manage.py setup_sendgrid --setup')
            return
            
        # Test connection
        self.stdout.write('Testing SMTP connectivity...')
        import socket
        try:
            socket.create_connection(('smtp.sendgrid.net', 587), timeout=10)
            self.stdout.write(self.style.SUCCESS('✅ Connection to SendGrid SMTP successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Connection failed: {str(e)}'))
            return
            
        # Test authentication
        self.stdout.write('Testing authentication...')
        try:
            import smtplib
            server = smtplib.SMTP('smtp.sendgrid.net', 587)
            server.starttls()
            server.login('apikey', settings.EMAIL_HOST_PASSWORD)
            server.quit()
            self.stdout.write(self.style.SUCCESS('✅ SendGrid authentication successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Authentication failed: {str(e)}'))
            self.stdout.write('Check your SENDGRID_API_KEY in Railway variables')
            return
            
        self.stdout.write(self.style.SUCCESS('\n🎉 SendGrid is ready to use!'))
        self.stdout.write('Test sending: python manage.py test_email --email your@email.com --type simple')
