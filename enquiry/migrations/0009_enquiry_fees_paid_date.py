# Generated by Django 5.2 on 2025-05-31 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enquiry', '0008_enquiry_other_subject_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='enquiry',
            name='fees_paid_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
