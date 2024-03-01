# Generated by Django 3.2.15 on 2024-03-01 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0016_alter_application_student_number"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="apt_number",
            field=models.CharField(
                blank=True, help_text="Apt number (Optional)", max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="application",
            name="region",
            field=models.CharField(help_text="Region/Province", max_length=255),
        ),
    ]
