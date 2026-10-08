import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("bd_models", "0014_alter_ball_options_alter_ballinstance_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CollectorType",
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
                ("name", models.CharField(max_length=64, unique=True)),
                (
                    "min",
                    models.IntegerField(
                        default=250,
                        help_text="Minimum ball count required (applied at rarity_min)",
                    ),
                ),
                (
                    "max",
                    models.IntegerField(
                        default=3500,
                        help_text="Maximum ball count required (applied at rarity_max)",
                    ),
                ),
                (
                    "gap",
                    models.IntegerField(
                        default=50,
                        help_text="Rounding step applied to the interpolated count requirement",
                    ),
                ),
                (
                    "rarity_min",
                    models.FloatField(
                        default=0.05,
                        help_text="Ball rarity value that maps to the minimum count requirement",
                    ),
                ),
                (
                    "rarity_max",
                    models.FloatField(
                        default=0.80,
                        help_text="Ball rarity value that maps to the maximum count requirement",
                    ),
                ),
                (
                    "source_special",
                    models.ForeignKey(
                        blank=True,
                        help_text="Only count balls with this special towards the requirement (null = count all balls)",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="collector_source_types",
                        to="bd_models.special",
                    ),
                ),
                ("enabled", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "collectortype",
                "managed": True,
            },
        ),
    ]
