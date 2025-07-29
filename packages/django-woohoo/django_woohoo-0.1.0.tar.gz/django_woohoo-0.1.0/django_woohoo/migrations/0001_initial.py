# django_woohoo/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion
import django.contrib.contenttypes.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),  # Needed for GenericForeignKey
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    choices=[
                        ('Amazon Authorization', 'Amazon Authorization'),
                        ('Amazon Bearer', 'Amazon Bearer'),
                        ('Flipkart Authorization', 'Flipkart Authorization'),
                        ('Flipkart Bearer', 'Flipkart Bearer')
                    ],
                    max_length=255,
                    unique=True
                )),
                ('token', models.TextField()),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlatformPaymentRequestLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_provider', models.CharField(
                    choices=[
                        ('Cashfree', 'Cashfree'),
                        ('Amazon', 'Amazon'),
                        ('Flipkart', 'Flipkart')
                    ],
                    max_length=100
                )),
                ('url', models.TextField()),
                ('body', models.TextField()),
                ('response', models.TextField()),
                ('response_status', models.PositiveIntegerField()),
                ('requested_user_object_id', models.CharField(max_length=100)),
                ('requested_user_frozen_details', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('requested_user_content_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='contenttypes.ContentType'
                )),
            ],
        ),
    ]
