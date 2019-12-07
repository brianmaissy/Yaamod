# Generated by Django 2.2.6 on 2019-11-30 18:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0004_add_scheduled_aliya_table'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='scheduledaliya',
            name='unique_scheduled_aliya',
        ),
        migrations.RemoveField(
            model_name='scheduledaliya',
            name='confirmed',
        ),
        migrations.AddField(
            model_name='scheduledaliya',
            name='mincha',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='scheduledaliya',
            name='aliya_number',
            field=models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddConstraint(
            model_name='scheduledaliya',
            constraint=models.UniqueConstraint(fields=('date', 'mincha', 'aliya_number'), name='unique_scheduled_aliya'),
        ),
    ]
