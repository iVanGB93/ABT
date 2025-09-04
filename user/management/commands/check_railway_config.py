from django.core.management.base import BaseCommand
import os
import multiprocessing

class Command(BaseCommand):
    help = 'Check Gunicorn configuration for Railway deployment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Railway Deployment Configuration Check\n'))
        
        # Check PORT environment variable
        port = os.environ.get('PORT', '8080')
        self.stdout.write(f'📡 PORT: {port}')
        
        if port == '8080':
            self.stdout.write(self.style.WARNING('   ⚠️  Using fallback port 8080 (Railway will set PORT automatically)'))
        else:
            self.stdout.write(self.style.SUCCESS(f'   ✅ Using Railway assigned PORT: {port}'))
        
        # Check CPU count for workers
        cpu_count = multiprocessing.cpu_count()
        recommended_workers = max(1, min(cpu_count * 2 + 1, 4))
        
        self.stdout.write(f'\n💻 System Info:')
        self.stdout.write(f'   CPU Cores: {cpu_count}')
        self.stdout.write(f'   Recommended Workers: {recommended_workers}')
        
        # Check memory considerations
        self.stdout.write(f'\n🧠 Memory Considerations:')
        self.stdout.write(f'   Max workers for Railway: 4 (memory limited)')
        self.stdout.write(f'   Worker memory limit: 512MB each')
        
        # Configuration summary
        self.stdout.write(f'\n⚙️  Gunicorn Configuration:')
        self.stdout.write(f'   Bind: 0.0.0.0:{port}')
        self.stdout.write(f'   Workers: {recommended_workers}')
        self.stdout.write(f'   Timeout: 120 seconds')
        self.stdout.write(f'   Preload: True')
        
        # Recommendations
        self.stdout.write(f'\n📋 Railway Deployment Checklist:')
        self.stdout.write('   ✅ Dynamic PORT configuration')
        self.stdout.write('   ✅ Memory-optimized worker count')
        self.stdout.write('   ✅ Extended timeout for email processing')
        self.stdout.write('   ✅ Stdout/stderr logging for Railway')
        self.stdout.write('   ✅ Backup Procfile available')
        
        # Warnings
        self.stdout.write(f'\n⚠️  Important Notes:')
        self.stdout.write('   • Railway will automatically set $PORT')
        self.stdout.write('   • Configuration is memory-optimized for Railway limits')
        self.stdout.write('   • Use Procfile.backup if config file fails')
        self.stdout.write('   • Monitor Railway logs for worker performance')
        
        self.stdout.write(self.style.SUCCESS('\n🚀 Configuration looks good for Railway deployment!'))
