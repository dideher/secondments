# Generated by Django 4.1.3 on 2022-11-10 11:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Municipality',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Όνομα Δήμου', max_length=128)),
                ('within_pysde', models.BooleanField(db_index=True, default=False, help_text='Εντός ΠΥΣΔΕ')),
            ],
        ),
        migrations.CreateModel(
            name='Prefecture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Όνομα Νομού', max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ministry_code', models.CharField(max_length=7)),
                ('name', models.CharField(max_length=80)),
                ('school_kind', models.CharField(max_length=80)),
                ('school_type', models.CharField(max_length=80)),
                ('telephone', models.CharField(max_length=32)),
                ('fax', models.CharField(blank=True, max_length=32)),
                ('email', models.CharField(max_length=64)),
                ('is_eaep', models.BooleanField(default=False)),
                ('is_nps', models.BooleanField(default=False)),
                ('address', models.CharField(blank=True, max_length=128)),
                ('zip_code', models.CharField(blank=True, max_length=12)),
                ('prefecture', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='commons.prefecture')),
            ],
        ),
        migrations.AddConstraint(
            model_name='prefecture',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_prefecture_name'),
        ),
        migrations.AddField(
            model_name='municipality',
            name='prefecture',
            field=models.ForeignKey(help_text='Νομός', on_delete=django.db.models.deletion.CASCADE, to='commons.prefecture'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['school_kind', 'school_type', 'prefecture'], name='commons_sch_school__b9ef59_idx'),
        ),
        migrations.AddConstraint(
            model_name='school',
            constraint=models.UniqueConstraint(fields=('ministry_code',), name='unique_school_ministry_code'),
        ),
        migrations.AddConstraint(
            model_name='school',
            constraint=models.UniqueConstraint(fields=('name',), name='unique_school_name'),
        ),
        migrations.AddIndex(
            model_name='municipality',
            index=models.Index(fields=['prefecture', 'name'], name='commons_mun_prefect_b83e3d_idx'),
        ),
        migrations.AddIndex(
            model_name='municipality',
            index=models.Index(fields=['within_pysde'], name='commons_mun_within__b0486a_idx'),
        ),
        migrations.AddConstraint(
            model_name='municipality',
            constraint=models.UniqueConstraint(fields=('prefecture', 'name'), name='unique_prefecture_and_name'),
        ),
    ]