# Generated by Django 5.1.2 on 2025-01-22 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agentoapp', '0009_remove_subtask_codeblock_remove_subtask_type_tool_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tool',
            name='belongs_to',
        ),
        migrations.AddField(
            model_name='tool',
            name='name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
