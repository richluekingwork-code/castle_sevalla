from django.db import migrations

MODEL_RENAMES = {
    'bookset': ('planset', 'plan set'),
    'volume': ('plandocument', 'plan document'),
}


def rename_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    for permission in Permission.objects.filter(content_type__app_label='plan_room'):
        action, _, model = permission.codename.partition('_')
        if model in MODEL_RENAMES:
            new_model, new_label = MODEL_RENAMES[model]
            permission.codename = f'{action}_{new_model}'
            permission.name = f'Can {action} {new_label}'
            permission.save()


def rename_access_type(apps, schema_editor):
    PlanSet = apps.get_model('plan_room', 'PlanSet')
    PlanSet.objects.filter(access_type='students').update(access_type='clients')


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('plan_room', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel('BookSet', 'PlanSet'),
        migrations.RenameModel('Volume', 'PlanDocument'),
        migrations.RenameField('PlanDocument', 'book_set', 'plan_set'),
        migrations.RenameField('PlanDocument', 'volume_number', 'document_number'),
        migrations.RenameField('Purchase', 'book_set', 'plan_set'),
        migrations.RenameField('PlanSet', 'author', 'prepared_by'),
        migrations.RenameField('UserProfile', 'is_student', 'is_client'),
        migrations.RunPython(rename_permissions, migrations.RunPython.noop),
        migrations.RunPython(rename_access_type, migrations.RunPython.noop),
    ]
