# Generated by Django 4.2.16 on 2024-10-15 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_remove_answersheet_answers_answersheet_is_correct_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='category',
            field=models.CharField(choices=[('math', 'Math'), ('science', 'Science'), ('geography', 'Geography'), ('testing', 'Testing')], max_length=50),
        ),
    ]
