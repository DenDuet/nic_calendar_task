from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from prjcalendar.permissions import (
    create_default_groups, 
    setup_default_permissions,
    create_user_profile_for_existing_users
)


class Command(BaseCommand):
    help = 'Настраивает систему прав доступа для пользователей'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-groups',
            action='store_true',
            help='Создать стандартные группы пользователей',
        )
        parser.add_argument(
            '--setup-permissions',
            action='store_true',
            help='Настроить стандартные права для групп',
        )
        parser.add_argument(
            '--create-profiles',
            action='store_true',
            help='Создать профили для существующих пользователей',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Выполнить все операции',
        )

    def handle(self, *args, **options):
        if options['all'] or options['create_groups']:
            self.stdout.write('Создание стандартных групп пользователей...')
            groups = create_default_groups()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Создано групп: {len(groups)}'
                )
            )
            for name, group in groups.items():
                self.stdout.write(f'  - {group.name}: {group.description}')

        if options['all'] or options['setup_permissions']:
            self.stdout.write('Настройка стандартных прав для групп...')
            setup_default_permissions()
            self.stdout.write(
                self.style.SUCCESS('Права для групп настроены')
            )

        if options['all'] or options['create_profiles']:
            self.stdout.write('Создание профилей для существующих пользователей...')
            count = create_user_profile_for_existing_users()
            self.stdout.write(
                self.style.SUCCESS(f'Создано профилей: {count}')
            )

        if not any([options['create_groups'], options['setup_permissions'], 
                   options['create_profiles'], options['all']]):
            self.stdout.write(
                self.style.WARNING(
                    'Используйте --help для просмотра доступных опций'
                )
            )



