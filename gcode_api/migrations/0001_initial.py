# Generated by Django 4.2.7 on 2025-07-07 07:44

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Full name of the user', max_length=255)),
                ('email', models.EmailField(help_text='Email address (unique identifier)', max_length=254, unique=True)),
                ('role', models.CharField(choices=[('student', 'Student'), ('lecturer', 'Lecturer'), ('hod', 'Head of Department'), ('dean', 'Dean'), ('researcher', 'Researcher'), ('visitor', 'Visitor'), ('other', 'Other')], default='student', help_text="User's role in the organization", max_length=20)),
                ('department', models.CharField(blank=True, help_text='Department or division', max_length=255, null=True)),
                ('faculty', models.CharField(blank=True, help_text='Faculty or school', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submitted_at', models.DateTimeField(default=django.utils.timezone.now, help_text='When the user first submitted data')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='SignatureData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('svg_data', models.TextField(help_text='Raw SVG data')),
                ('gcode_data', models.TextField(help_text='Generated G-code')),
                ('gcode_metadata', models.JSONField(default=dict, help_text='Metadata about the G-code (lines, size, etc.)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(help_text='User who submitted this signature', on_delete=django.db.models.deletion.CASCADE, related_name='signatures', to='gcode_api.user')),
            ],
            options={
                'verbose_name': 'Signature Data',
                'verbose_name_plural': 'Signature Data',
                'ordering': ['-created_at'],
            },
        ),
    ]
