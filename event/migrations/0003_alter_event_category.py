# Generated by Django 5.1.3 on 2024-12-19 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("event", "0002_category_event_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="events",
                to="event.category",
            ),
        ),
    ]
