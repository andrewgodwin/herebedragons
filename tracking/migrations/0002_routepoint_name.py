# Generated by Django 4.2.3 on 2023-07-24 20:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracking", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="routepoint",
            name="name",
            field=models.CharField(default="name"),
            preserve_default=False,
        ),
    ]