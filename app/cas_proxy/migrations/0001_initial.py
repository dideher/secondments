# Generated by Django 4.1.3 on 2022-12-19 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SessionTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=1024)),
                ('ticket', models.CharField(max_length=1024)),
            ],
        ),
    ]
