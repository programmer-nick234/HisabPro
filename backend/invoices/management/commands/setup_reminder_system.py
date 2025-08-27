"""
Management command to set up the reminder system for existing users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from invoices.reminder_templates import setup_reminder_system_for_user


class Command(BaseCommand):
    help = 'Set up reminder system for existing users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='Set up reminder system for specific user ID',
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Set up reminder system for all users',
        )

    def handle(self, *args, **options):
        if options['user_id']:
            try:
                user = User.objects.get(id=options['user_id'])
                result = setup_reminder_system_for_user(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully set up reminder system for user {user.username}: '
                        f'{result["templates_created"]} templates, {result["rules_created"]} rules created'
                    )
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User with ID {options["user_id"]} not found')
                )
        
        elif options['all_users']:
            users = User.objects.all()
            total_users = users.count()
            success_count = 0
            
            for user in users:
                try:
                    result = setup_reminder_system_for_user(user)
                    success_count += 1
                    self.stdout.write(
                        f'✓ Set up for {user.username}: '
                        f'{result["templates_created"]} templates, {result["rules_created"]} rules'
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed for {user.username}: {str(e)}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCompleted: {success_count}/{total_users} users successfully set up'
                )
            )
        
        else:
            self.stdout.write(
                self.style.ERROR('Please specify either --user-id or --all-users')
            )
