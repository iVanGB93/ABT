from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Configure Django Sites for production'

    def handle(self, *args, **options):
        try:
            # Update or create the site
            site, created = Site.objects.get_or_create(id=1)
            
            if settings.DEBUG:
                site.domain = '127.0.0.1:8000'
                site.name = 'ABT Development'
            else:
                site.domain = 'abt.qbared.com'
                site.name = 'ABT - Advance Business Tools'
            
            site.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Site created: {site.domain}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Site updated: {site.domain}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error configuring site: {str(e)}'))
