# Generated by Django 2.2.16 on 2022-11-22 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'User'), ('moderator', 'Moderator'), ('admin', 'Administrator')], default='user', max_length=10, verbose_name='Роль'),
        ),
    ]
