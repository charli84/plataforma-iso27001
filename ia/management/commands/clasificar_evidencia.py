from django.core.management.base import BaseCommand, CommandError
from evidencias.models import Evidencia
from ia.utils import clasificar_evidencia_ia


class Command(BaseCommand):
    help = "Clasifica una evidencia usando IA (Claude) y guarda el resultado en Evaluacion."

    def add_arguments(self, parser):
        parser.add_argument("evidencia_id", type=int)

    def handle(self, *args, **options):
        evidencia_id = options["evidencia_id"]

        try:
            evidencia = Evidencia.objects.select_related("control", "cliente").get(id=evidencia_id)
        except Evidencia.DoesNotExist:
            raise CommandError(f"No existe una Evidencia con id={evidencia_id}")

        evaluacion = clasificar_evidencia_ia(evidencia)

        self.stdout.write(self.style.SUCCESS(
            f"Evidencia {evidencia_id} clasificada: {evaluacion.cumplimiento} (calificación {evaluacion.calificacion})"
        ))