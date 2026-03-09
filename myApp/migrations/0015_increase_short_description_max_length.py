# Generated for fix: value too long for type character varying(300)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0014_increase_slug_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='short_description',
            field=models.CharField(max_length=1000),
        ),
    ]
