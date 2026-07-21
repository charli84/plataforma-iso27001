from django.core.management.base import BaseCommand, CommandError
from evidencias.models import Evidencia
from ia.models import Evaluacion
from ia.utils import extraer_texto
import anthropic

MODEL = "claude-haiku-4-5-20251001"


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

        control = evidencia.control
        texto = extraer_texto(evidencia.archivo)

        prompt = f"""Eres un auditor experto en ISO/IEC 27001 e ISO/IEC 27002:2022.

Analiza si el siguiente documento de evidencia cumple con el control:

Código de control: {control.codigo}
Nombre del control: {control.nombre}
Descripción del control: {control.descripcion}

Contenido del documento de evidencia:
\"\"\"
{texto}
\"\"\"

Responde EXACTAMENTE en este formato, sin texto adicional:
CUMPLIMIENTO: [CUMPLE|PARCIAL|NO_CUMPLE|PENDIENTE]
CALIFICACION: [número del 1 al 10]
RECOMENDACIONES: [texto breve con recomendaciones concretas]
"""

        client = anthropic.Anthropic()
        respuesta = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        texto_respuesta = respuesta.content[0].text

        cumplimiento = "PENDIENTE"
        calificacion = None
        recomendaciones = ""

        for linea in texto_respuesta.splitlines():
            linea = linea.strip()
            if linea.startswith("CUMPLIMIENTO:"):
                cumplimiento = linea.replace("CUMPLIMIENTO:", "").strip()
            elif linea.startswith("CALIFICACION:"):
                valor = linea.replace("CALIFICACION:", "").strip()
                try:
                    calificacion = int(valor)
                except ValueError:
                    calificacion = None
            elif linea.startswith("RECOMENDACIONES:"):
                recomendaciones = linea.replace("RECOMENDACIONES:", "").strip()

        Evaluacion.objects.update_or_create(
            evidencia=evidencia,
            defaults={
                "cumplimiento": cumplimiento,
                "calificacion": calificacion,
                "recomendaciones": recomendaciones,
                "modelo_ia": MODEL,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            f"Evidencia {evidencia_id} clasificada: {cumplimiento} (calificación {calificacion})"
        ))

