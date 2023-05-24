# Generated by Django 4.1.7 on 2023-05-02 17:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audit", "0021_alter_singleauditchecklist_submission_status"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="access",
            name="audit_$(class)s_single_creator",
        ),
        migrations.AlterField(
            model_name="access",
            name="role",
            field=models.CharField(
                choices=[
                    ("certifying_auditee_contact ", "Auditee Certifying Official"),
                    ("certifying_auditor_contact ", "Auditor Certifying Official"),
                    ("editor", "Audit Editor"),
                ],
                help_text="Access type granted to this user",
                max_length=50,
            ),
        ),
    ]
