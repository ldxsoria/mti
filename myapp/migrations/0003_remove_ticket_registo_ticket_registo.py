# Generated by Django 4.1.3 on 2022-11-16 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_alter_ticket_registo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='registo',
        ),
        migrations.AddField(
            model_name='ticket',
            name='registo',
            field=models.ManyToManyField(null=True, to='myapp.registroticket'),
        ),
    ]
