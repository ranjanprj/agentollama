# Generated by Django 5.1.6 on 2025-03-21 15:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentoapp', '0028_alter_knowledgerep_associated_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledgerep',
            name='associated_task',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='agentoapp.task'),
        ),
    ]
