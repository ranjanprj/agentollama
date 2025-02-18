# Generated by Django 5.1.2 on 2025-02-01 21:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentoapp', '0014_tasklog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tasklog',
            name='task',
        ),
        migrations.CreateModel(
            name='TaskRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='agentoapp.task')),
            ],
        ),
        migrations.AddField(
            model_name='tasklog',
            name='task_run',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='agentoapp.taskrun'),
            preserve_default=False,
        ),
    ]
