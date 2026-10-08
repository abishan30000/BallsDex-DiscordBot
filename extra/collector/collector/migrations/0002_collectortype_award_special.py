import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bd_models", "0014_alter_ball_options_alter_ballinstance_options_and_more"),
        ("collector", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectortype",
            name="award_special",
            field=models.ForeignKey(
                blank=True,
                help_text="The special applied to the awarded ball",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="collector_award_types",
                to="bd_models.special",
            ),
        ),
    ]
