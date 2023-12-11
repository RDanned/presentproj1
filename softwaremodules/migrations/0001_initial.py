from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shopcore', '0084_alter_sitesettings_locale'),
        ('user', '0081_profile_amount_left'),
    ]

    operations = [
        migrations.CreateModel(
            name='Softwaremodule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation time')),
                ('time_updated', models.DateTimeField(auto_now=True, null=True, verbose_name='update time')),
                ('time_deleted', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='deletion time')),
                ('ip_created', models.GenericIPAddressField(blank=True, editable=False, null=True, verbose_name='created by ip')),
                ('ip_updated', models.GenericIPAddressField(blank=True, editable=False, null=True, verbose_name='updated by ip')),
                ('ip_deleted', models.GenericIPAddressField(blank=True, editable=False, null=True, verbose_name='deleted by ip')),
                ('published', models.BooleanField(default=True, verbose_name='is published')),
                ('published_since', models.DateTimeField(blank=True, null=True, verbose_name='published since date')),
                ('published_till', models.DateTimeField(blank=True, null=True, verbose_name='published till date')),
                ('auth_needed', models.BooleanField(default=False, verbose_name='auth needed')),
                ('code', models.CharField(choices=[('module', 'Module')], max_length=255, verbose_name='code')),
                ('data', models.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('site', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='shopcore.sitesettings', verbose_name='site')),
                ('site_original', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='shopcore.sitesettings', verbose_name='site original')),
                ('site_settings', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shopcore.sitesettings')),
                ('user_created', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='user.profile', verbose_name='created by user')),
                ('user_deleted', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='user.profile', verbose_name='deleted by user')),
                ('user_updated', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='user.profile', verbose_name='updated by user')),
            ],
            options={
                'verbose_name': 'softwaremodule',
                'verbose_name_plural': 'softwaremodules',
            },
        ),
    ]
