# Generated for fix: value too long for type character varying(50)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0013_add_ai_chatbot_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='bundle',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
    ]
