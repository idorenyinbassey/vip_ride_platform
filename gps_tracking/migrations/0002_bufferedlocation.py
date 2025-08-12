# Generated migration for BufferedLocation model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("gps_tracking", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BufferedLocation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
                ("timestamp", models.DateTimeField()),
                ("accuracy", models.FloatField(default=0)),
                ("altitude", models.FloatField(blank=True, null=True)),
                ("bearing", models.FloatField(blank=True, null=True)),
                ("speed_kmh", models.FloatField(blank=True, null=True)),
                ("battery_level", models.IntegerField(blank=True, null=True)),
                (
                    "buffer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buffered_points",
                        to="gps_tracking.offlinegpsbuffer",
                    ),
                ),
            ],
            options={
                "db_table": "buffered_locations",
            },
        ),
        migrations.AddIndex(
            model_name="bufferedlocation",
            index=models.Index(fields=["buffer"], name="gps_buffer_idx"),
        ),
        migrations.AddIndex(
            model_name="bufferedlocation",
            index=models.Index(fields=["timestamp"], name="gps_timestamp_idx"),
        ),
    ]
