# Generated by Django 4.2.3 on 2023-07-24 23:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracking", "0002_routepoint_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="route",
            name="ends",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="route",
            name="starts",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
