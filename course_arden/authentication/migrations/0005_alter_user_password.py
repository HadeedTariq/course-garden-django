# Generated by Django 5.1.3 on 2024-11-30 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_otp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
