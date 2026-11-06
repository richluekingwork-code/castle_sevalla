from django.core.management.base import BaseCommand
from django.db import connection

LEGACY_APPS = {'clrSite': 'castle_site', 'libraryApp': 'plan_room'}


class Command(BaseCommand):
    help = 'Move tables and migration history from the old app names to the new ones. Safe to run repeatedly; must run before migrate.'

    def handle(self, *args, **kwargs):
        tables = connection.introspection.table_names()
        if 'django_migrations' not in tables:
            self.stdout.write('Fresh database, nothing to rename.')
            return

        with connection.schema_editor() as editor:
            for old_label, new_label in LEGACY_APPS.items():
                for table in tables:
                    if table.startswith(f'{old_label}_'):
                        new_table = new_label + table[len(old_label):]
                        editor.alter_db_table(None, table, new_table)
                        self.stdout.write(f'{table} -> {new_table}')
                editor.execute('UPDATE django_migrations SET app = %s WHERE app = %s', [new_label, old_label])
                if 'django_content_type' in tables:
                    editor.execute('UPDATE django_content_type SET app_label = %s WHERE app_label = %s', [new_label, old_label])
        self.stdout.write(self.style.SUCCESS('Legacy app names are up to date.'))
