# Generated by Django 4.1 on 2022-09-01 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0004_remove_transaction_date_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, default='2022-09-01 19:08:02'),
            preserve_default=False,
        ),
    ]
