from django.db import migrations

# No usamos pgvector.django.VectorExtension: en pgvector-python 0.3.6
# (la única versión de esa librería compatible con Python 3.13 al momento
# de escribir esto) esa clase no llama correctamente al __init__ de la
# operación base de Django, y con Django 6.0 revienta con
# "AttributeError: 'VectorExtension' object has no attribute 'hints'".
# Creamos la extensión con SQL directo para evitar ese bug.


class Migration(migrations.Migration):

    dependencies = [
        ("controles", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS vector;",
            reverse_sql="DROP EXTENSION IF EXISTS vector;",
        ),
    ]
