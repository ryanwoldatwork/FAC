# Generated by Django 4.2.5 on 2023-10-06 16:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffUser",
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
                ("staff_email", models.EmailField(max_length=254)),
                (
                    "date_added",
                    models.DateTimeField(auto_now_add=True, verbose_name="Date Added"),
                ),
                (
                    "added_by_email",
                    models.EmailField(max_length=254, verbose_name="Email of Adder"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StaffUserLog",
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
                ("staff_email", models.EmailField(max_length=254)),
                (
                    "date_added",
                    models.DateTimeField(auto_now_add=True, verbose_name="Date Added"),
                ),
                (
                    "added_by_email",
                    models.EmailField(max_length=254, verbose_name="Email of Adder"),
                ),
                (
                    "date_removed",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Date removed"
                    ),
                ),
                (
                    "removed_by_email",
                    models.EmailField(max_length=254, verbose_name="Email of Remover"),
                ),
            ],
        ),
    ]
