# Generated by Django 2.0.3 on 2018-05-15 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innovations', '0003_violationreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='innovation',
            name='description',
            field=models.TextField(max_length=1024),
        ),
    ]
