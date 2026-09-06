from django.core.management.base import BaseCommand

from controles.models import Control
from ia.embeddings import embed_query


class Command(BaseCommand):
    help = (
        "Precalcula el embedding semantico (codigo + nombre + descripcion) de cada "
        "control ISO/IEC 27002 y lo guarda en la base de datos. Se usa como paso "
        "previo para la busqueda RAG al evaluar evidencia con IA. Correr de nuevo "
        "cada vez que cambien las descripciones de los controles."
    )

    def handle(self, *args, **options):
        controles = Control.objects.all()
        total = controles.count()

        if total == 0:
            self.stdout.write(self.style.WARNING(
                "No hay controles cargados. Corre primero: python manage.py cargar_controles_iso"
            ))
            return

        actualizados = 0
        for control in controles:
            texto = f"{control.codigo} {control.nombre}. {control.descripcion}".strip()
            control.embedding = embed_query(texto)
            control.save(update_fields=["embedding"])
            actualizados += 1
            self.stdout.write(f"  {control.codigo} listo ({actualizados}/{total})")

        self.stdout.write(self.style.SUCCESS(
            f"Embeddings generados para {actualizados}/{total} controles."
        ))
