# Generated by Django 2.0.3 on 2018-06-13 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('innovations', '0004_innovation_description_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='innovation',
            name='assumptions',
            field=models.TextField(max_length=1024),
        ),
    ]
