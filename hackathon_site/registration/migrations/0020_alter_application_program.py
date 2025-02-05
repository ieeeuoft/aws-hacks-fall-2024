# Generated by Django 3.2.15 on 2024-03-02 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registration", "0019_auto_20240301_1145"),
    ]

    operations = [
        migrations.AlterField(
            model_name="application",
            name="program",
            field=models.CharField(
                choices=[
                    (None, ""),
                    ("chemical-engineering", "Chemical Engineering"),
                    ("civil-engineering", "Civil Engineering"),
                    ("computer-science", "Computer Science"),
                    ("electrical-engineering", "Electrical Engineering"),
                    ("computer-engineering", "Computer Engineering"),
                    ("engineering-science", "Engineering Science"),
                    ("industrial-engineering", "Industrial Engineering"),
                    ("mechanical-engineering", "Mechanical Engineering"),
                    ("materials-engineering", "Materials Engineering"),
                    ("mineral-engineering", "Mineral Engineering"),
                    ("track-one", "TrackOne"),
                ],
                max_length=50,
            ),
        ),
    ]
