from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0017_courseresource'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentIPLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('date_bucket', models.DateField(default=django.utils.timezone.localdate, help_text='Day-level bucket to limit duplicates')),
                ('country', models.CharField(blank=True, max_length=100)),
                ('region', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('is_private_ip', models.BooleanField(default=False)),
                ('hit_count', models.PositiveIntegerField(default=1)),
                ('last_path', models.CharField(blank=True, max_length=300)),
                ('user_agent', models.TextField(blank=True)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ip_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-last_seen'],
                'unique_together': {('user', 'ip_address', 'date_bucket')},
            },
        ),
        migrations.AddIndex(
            model_name='studentiplog',
            index=models.Index(fields=['ip_address', 'last_seen'], name='myApp_stude_ip_addr_4caec5_idx'),
        ),
        migrations.AddIndex(
            model_name='studentiplog',
            index=models.Index(fields=['date_bucket', 'last_seen'], name='myApp_stude_date_bu_301dc2_idx'),
        ),
        migrations.AddIndex(
            model_name='studentiplog',
            index=models.Index(fields=['user', 'last_seen'], name='myApp_stude_user_id_611139_idx'),
        ),
    ]
