# Generated by Django 5.2 on 2025-05-05 13:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Counsellor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('mobile', models.CharField(max_length=15)),
                ('department', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Enquiry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('mobile', models.CharField(max_length=15)),
                ('subject', models.CharField(choices=[('java_full_stack', 'Java Full Stack'), ('python_full_stack', 'Python Full Stack'), ('other', 'Other')], max_length=50)),
                ('status', models.CharField(choices=[('joined', 'Joined'), ('pending', 'Pending'), ('dropout', 'Dropout')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('counsellor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='enquiry.counsellor')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('followup_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('enquiry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='enquiry.enquiry')),
            ],
        ),
    ]
