# Generated by Django 5.1.3 on 2024-12-19 12:43

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("event", "0003_alter_event_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="private_key",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
