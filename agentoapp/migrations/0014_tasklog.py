# Generated by Django 5.1.2 on 2025-02-01 20:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentoapp', '0013_remove_subtask_current_step_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.TextField()),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='agentoapp.task')),
            ],
        ),
    ]
