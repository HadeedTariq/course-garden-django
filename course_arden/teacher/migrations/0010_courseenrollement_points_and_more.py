# Generated by Django 5.1.3 on 2024-12-12 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teacher', '0009_alter_courseenrollement_course_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseenrollement',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelTable(
            name='courseenrollement',
            table='courseenrollements',
        ),
        migrations.DeleteModel(
            name='CoursePoints',
        ),
    ]
