# Generated by Django 5.1.2 on 2025-01-12 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentoapp', '0003_task_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtask',
            name='description',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subtask',
            name='name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.CharField(max_length=100),
        ),
    ]
