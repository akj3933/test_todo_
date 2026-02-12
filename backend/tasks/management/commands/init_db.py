from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Initialize database with test data'

    def handle(self, *args, **kwargs):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin/admin123'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))
        
        # Create test user if it doesn't exist
        if not User.objects.filter(username='testuser').exists():
            User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='test123'
            )
            self.stdout.write(self.style.SUCCESS('Created test user: testuser/test123'))
        else:
            self.stdout.write(self.style.WARNING('Test user already exists'))
