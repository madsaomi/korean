from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_streak_last_active_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='streak',
            name='last_active_date',
            field=models.DateField(blank=True, null=True, default=None),
        ),
    ]
