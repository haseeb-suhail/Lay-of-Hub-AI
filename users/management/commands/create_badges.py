from django.core.management.base import BaseCommand
from users.models import Badge

class Command(BaseCommand):
    help = 'Create initial badges'

    def handle(self, *args, **kwargs):
        badges = [
            {'name': 'Layoff Whisperer', 'description': 'Start at 0 points'},
            {'name': 'Contributor', 'description': 'Awarded at 50 points'},
            {'name': 'Rumor Connoisseur', 'description': 'Awarded at 100 points'},
            {'name': 'Master of Scuttlebutt', 'description': 'Awarded at 250 points'},
            {'name': 'Guru', 'description': 'Awarded at 500 points'},
            {'name': 'Elder', 'description': 'Awarded at 1000 points'},
            {'name': 'Oracle', 'description': 'Awarded at 5000 points'},
        ]

        for badge_data in badges:
            Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults={
                    'description': badge_data['description']
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully created badges'))
