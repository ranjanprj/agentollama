# Generated by Django 5.1.2 on 2025-02-06 05:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentoapp', '0017_knowledgerep_knowledgerepfiles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledgerepfiles',
            name='Knowledge_rep',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='agentoapp.knowledgerep'),
        ),
    ]
