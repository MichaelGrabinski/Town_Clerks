"""Initial migration for app-owned tables only.

IMPORTANT: Do not include legacy tables here. Legacy tables are unmanaged and live in other DBs.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('username', models.CharField(blank=True, default='', max_length=150)),
                ('event_type', models.CharField(db_index=True, max_length=50)),
                ('action', models.CharField(blank=True, default='', max_length=200)),
                ('path', models.CharField(blank=True, default='', max_length=500)),
                ('method', models.CharField(blank=True, default='', max_length=10)),
                ('status_code', models.IntegerField(blank=True, null=True)),
                ('ip_address', models.CharField(blank=True, default='', max_length=64)),
                ('user_agent', models.TextField(blank=True, default='')),
                ('referer', models.CharField(blank=True, default='', max_length=500)),
                ('query_string', models.TextField(blank=True, default='')),
                ('extra', models.JSONField(blank=True, null=True)),
                (
                    'user',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='town_clerks_activity_logs',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
