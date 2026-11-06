from django.db import migrations

MODEL_RENAMES = {
    'testimonyandsayings': ('clienttestimonial', 'client testimonial'),
    'targetedaudience': ('clienttype', 'client type'),
    'targetaudience': ('clientsector', 'client sector'),
    'programs': ('companyresource', 'company resource'),
    'donations': ('paymentaccount', 'payment account'),
    'donation': ('clientpayment', 'client payment'),
}
CATEGORY_RENAMES = {'research': 'technical', 'education': 'safety'}


def rename_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    for permission in Permission.objects.filter(content_type__app_label='castle_site'):
        action, _, model = permission.codename.partition('_')
        if model in MODEL_RENAMES:
            new_model, new_label = MODEL_RENAMES[model]
            permission.codename = f'{action}_{new_model}'
            permission.name = f'Can {action} {new_label}'
            permission.save()


def rename_categories(apps, schema_editor):
    CompanyResource = apps.get_model('castle_site', 'CompanyResource')
    for old, new in CATEGORY_RENAMES.items():
        CompanyResource.objects.filter(category=old).update(category=new)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('castle_site', '0006_migrate_projects_fields'),
    ]

    operations = [
        migrations.RenameModel('TestimonyAndSayings', 'ClientTestimonial'),
        migrations.RenameModel('TargetedAudience', 'ClientType'),
        migrations.RenameModel('TargetAudience', 'ClientSector'),
        migrations.RenameModel('Programs', 'CompanyResource'),
        migrations.RenameModel('Donations', 'PaymentAccount'),
        migrations.RenameModel('Donation', 'ClientPayment'),
        migrations.RenameField('ClientPayment', 'donor_name', 'client_name'),
        migrations.RunPython(rename_permissions, migrations.RunPython.noop),
        migrations.RunPython(rename_categories, migrations.RunPython.noop),
    ]
