from django.core.management.base import BaseCommand
from controles.models import Control

# Catalogo completo de los 93 controles de ISO/IEC 27002:2022,
# agrupados en los 4 temas de la norma:
# ORG = Organizacional (5.1-5.37), PER = Personas (6.1-6.8),
# FIS = Fisico (7.1-7.14), TEC = Tecnologico (8.1-8.34)
#
# Las descripciones son un resumen propio (parafraseado) del objetivo de cada
# control, escrito para dar contexto a la evaluacion con IA. No son una copia
# del texto oficial de la norma ISO/IEC 27002:2022 (protegido por derechos de
# autor); son una explicacion original, breve, del alcance de cada control.
CONTROLES = [
    # Organizacionales
    ("5.1", "Políticas de seguridad de la información", "ORG",
     "Definir, aprobar por la dirección, publicar y revisar periódicamente un conjunto de políticas de seguridad de la información alineadas con los objetivos del negocio."),
    ("5.2", "Roles y responsabilidades de seguridad de la información", "ORG",
     "Definir y asignar claramente los roles y responsabilidades de seguridad de la información dentro de la organización."),
    ("5.3", "Segregación de funciones", "ORG",
     "Separar tareas y áreas de responsabilidad en conflicto para reducir el riesgo de uso indebido o modificación no autorizada de los activos de la organización."),
    ("5.4", "Responsabilidades de la dirección", "ORG",
     "Exigir que la dirección promueva activamente el cumplimiento de las políticas y procedimientos de seguridad de la información por parte de todo el personal."),
    ("5.5", "Contacto con las autoridades", "ORG",
     "Mantener contacto formal con las autoridades pertinentes (policía, reguladores, organismos de emergencia) para casos relacionados con seguridad de la información."),
    ("5.6", "Contacto con grupos de interés especial", "ORG",
     "Mantener contacto con grupos de interés especial, foros y asociaciones profesionales de seguridad para estar al tanto de amenazas y buenas prácticas."),
    ("5.7", "Inteligencia de amenazas", "ORG",
     "Recopilar y analizar información sobre amenazas a la seguridad de la información para tomar acciones de mitigación oportunas."),
    ("5.8", "Seguridad de la información en la gestión de proyectos", "ORG",
     "Integrar la seguridad de la información en la gestión de proyectos, sin importar el tipo de proyecto."),
    ("5.9", "Inventario de información y otros activos asociados", "ORG",
     "Elaborar y mantener un inventario de la información y otros activos asociados, incluyendo a sus propietarios."),
    ("5.10", "Uso aceptable de la información y otros activos asociados", "ORG",
     "Identificar, documentar e implementar reglas para el uso aceptable y los procedimientos de manejo de la información y otros activos asociados."),
    ("5.11", "Devolución de activos", "ORG",
     "Exigir que el personal y otras partes interesadas devuelvan todos los activos de la organización que tengan en su posesión al finalizar su empleo, contrato o acuerdo."),
    ("5.12", "Clasificación de la información", "ORG",
     "Clasificar la información según las necesidades de confidencialidad, integridad, disponibilidad y los requisitos de las partes interesadas."),
    ("5.13", "Etiquetado de la información", "ORG",
     "Desarrollar e implementar procedimientos adecuados de etiquetado de información, de acuerdo con el esquema de clasificación adoptado."),
    ("5.14", "Transferencia de información", "ORG",
     "Establecer reglas, procedimientos y acuerdos de transferencia de información para todo tipo de transferencia dentro y fuera de la organización."),
    ("5.15", "Control de acceso", "ORG",
     "Establecer e implementar reglas para controlar el acceso físico y lógico a la información y otros activos asociados, basadas en requisitos del negocio y seguridad."),
    ("5.16", "Gestión de identidad", "ORG",
     "Gestionar el ciclo de vida completo de las identidades para permitir la asignación adecuada de derechos de acceso."),
    ("5.17", "Información de autenticación", "ORG",
     "Controlar la asignación y gestión de la información de autenticación mediante un proceso de gestión que incluya el asesoramiento al personal sobre su manejo adecuado."),
    ("5.18", "Derechos de acceso", "ORG",
     "Proporcionar, revisar, modificar y eliminar los derechos de acceso a la información y otros activos asociados según la política de control de acceso de la organización."),
    ("5.19", "Seguridad de la información en las relaciones con proveedores", "ORG",
     "Definir e implementar procesos y procedimientos para gestionar los riesgos de seguridad de la información asociados al uso de productos o servicios de proveedores."),
    ("5.20", "Tratamiento de la seguridad de la información en los acuerdos con proveedores", "ORG",
     "Establecer y acordar con cada proveedor los requisitos de seguridad de la información pertinentes, según el tipo de relación con dicho proveedor."),
    ("5.21", "Gestión de la seguridad de la información en la cadena de suministro de TIC", "ORG",
     "Definir e implementar procesos y procedimientos para gestionar los riesgos de seguridad de la información asociados a la cadena de suministro de productos y servicios de TIC."),
    ("5.22", "Seguimiento, revisión y gestión de cambios de los servicios de proveedores", "ORG",
     "Monitorear, revisar, evaluar y gestionar de forma periódica los cambios en las prácticas de seguridad de la información de los proveedores y en la prestación de sus servicios."),
    ("5.23", "Seguridad de la información para el uso de servicios en la nube", "ORG",
     "Establecer procesos para la adquisición, uso, gestión y salida de servicios en la nube, de acuerdo con los requisitos de seguridad de la información de la organización."),
    ("5.24", "Planificación y preparación de la gestión de incidentes de seguridad de la información", "ORG",
     "Planificar y preparar la gestión de incidentes de seguridad de la información definiendo, estableciendo y comunicando procesos, roles y responsabilidades."),
    ("5.25", "Evaluación y decisión sobre los eventos de seguridad de la información", "ORG",
     "Evaluar los eventos de seguridad de la información y decidir si deben clasificarse como incidentes de seguridad de la información."),
    ("5.26", "Respuesta a incidentes de seguridad de la información", "ORG",
     "Responder a los incidentes de seguridad de la información de acuerdo con procedimientos documentados."),
    ("5.27", "Aprendizaje de los incidentes de seguridad de la información", "ORG",
     "Utilizar el conocimiento adquirido de los incidentes de seguridad de la información para fortalecer y mejorar los controles de seguridad."),
    ("5.28", "Recopilación de evidencia", "ORG",
     "Establecer e implementar procedimientos para la identificación, recopilación, adquisición y preservación de evidencia relacionada con eventos de seguridad de la información."),
    ("5.29", "Seguridad de la información durante la interrupción", "ORG",
     "Planificar cómo mantener la seguridad de la información en el nivel adecuado durante una interrupción del negocio (por ejemplo, una crisis o desastre)."),
    ("5.30", "Preparación de las TIC para la continuidad del negocio", "ORG",
     "Planificar, implementar, mantener y probar la disponibilidad de la infraestructura de TIC para cumplir con los requisitos de continuidad del negocio."),
    ("5.31", "Requisitos legales, estatutarios, reglamentarios y contractuales", "ORG",
     "Identificar, documentar y mantener actualizados los requisitos legales, estatutarios, reglamentarios y contractuales pertinentes a la seguridad de la información."),
    ("5.32", "Derechos de propiedad intelectual", "ORG",
     "Implementar procedimientos adecuados para proteger los derechos de propiedad intelectual y cumplir con los requisitos legales y contractuales relacionados."),
    ("5.33", "Protección de los registros", "ORG",
     "Proteger los registros contra pérdida, destrucción, falsificación, acceso no autorizado y divulgación no autorizada."),
    ("5.34", "Privacidad y protección de datos personales", "ORG",
     "Identificar y cumplir los requisitos relacionados con la preservación de la privacidad y la protección de los datos personales, según las leyes y regulaciones aplicables."),
    ("5.35", "Revisión independiente de la seguridad de la información", "ORG",
     "Revisar de forma independiente y a intervalos planificados (o tras cambios significativos) el enfoque de la organización para gestionar la seguridad de la información."),
    ("5.36", "Cumplimiento de las políticas, reglas y normas de seguridad de la información", "ORG",
     "Revisar periódicamente el cumplimiento de la política, las reglas específicas por tema y los estándares de seguridad de la información de la organización."),
    ("5.37", "Procedimientos operativos documentados", "ORG",
     "Documentar los procedimientos de operación de las instalaciones de procesamiento de información y ponerlos a disposición del personal que los necesite."),
    # Personas
    ("6.1", "Investigación de antecedentes", "PER",
     "Realizar verificaciones de antecedentes de los candidatos a un puesto de trabajo, de acuerdo con las leyes, regulaciones y ética aplicables, y proporcionales al riesgo del cargo."),
    ("6.2", "Términos y condiciones del empleo", "PER",
     "Establecer en los acuerdos contractuales con el personal sus responsabilidades y las de la organización en materia de seguridad de la información."),
    ("6.3", "Concienciación, educación y capacitación en seguridad de la información", "PER",
     "Asegurar que el personal y las partes interesadas relevantes reciban formación y actualizaciones periódicas sobre la política de seguridad de la información y los procedimientos pertinentes a su función."),
    ("6.4", "Proceso disciplinario", "PER",
     "Formalizar y comunicar un proceso disciplinario para tomar medidas contra el personal y otras partes interesadas que hayan cometido una violación de la política de seguridad de la información."),
    ("6.5", "Responsabilidades tras la finalización o cambio de empleo", "PER",
     "Definir y hacer cumplir las responsabilidades y obligaciones de seguridad de la información que permanecen vigentes tras la finalización o cambio de empleo."),
    ("6.6", "Acuerdos de confidencialidad o no divulgación", "PER",
     "Identificar, documentar, revisar periódicamente y firmar acuerdos de confidencialidad o no divulgación que reflejen las necesidades de protección de la información."),
    ("6.7", "Trabajo remoto", "PER",
     "Implementar medidas de seguridad cuando el personal trabaja de forma remota, para proteger la información a la que accede, procesa o almacena fuera de las instalaciones de la organización."),
    ("6.8", "Reporte de eventos de seguridad de la información", "PER",
     "Proveer un mecanismo para que el personal reporte de forma oportuna los eventos de seguridad de la información observados o sospechados."),
    # Fisicos
    ("7.1", "Perímetros de seguridad física", "FIS",
     "Definir y utilizar perímetros de seguridad para proteger las áreas que contienen información y otros activos asociados."),
    ("7.2", "Controles de entrada física", "FIS",
     "Proteger las áreas seguras mediante controles de entrada y puntos de acceso adecuados, limitando el ingreso solo a personal autorizado."),
    ("7.3", "Protección de oficinas, despachos y recursos", "FIS",
     "Diseñar e implementar medidas de seguridad física para oficinas, despachos y otras instalaciones que contengan información o activos sensibles."),
    ("7.4", "Monitoreo de la seguridad física", "FIS",
     "Monitorear continuamente las instalaciones para detectar accesos físicos no autorizados."),
    ("7.5", "Protección contra amenazas físicas y ambientales", "FIS",
     "Diseñar e implementar protección contra amenazas físicas y ambientales como desastres naturales, ataques maliciosos o accidentes."),
    ("7.6", "Trabajo en áreas seguras", "FIS",
     "Diseñar e implementar medidas de seguridad para trabajar en áreas seguras."),
    ("7.7", "Escritorio y pantalla despejados", "FIS",
     "Establecer y hacer cumplir reglas de escritorio despejado para documentos en papel y medios de almacenamiento removibles, y de pantalla despejada para las instalaciones de procesamiento de información."),
    ("7.8", "Emplazamiento y protección de equipos", "FIS",
     "Ubicar y proteger los equipos de forma segura para reducir los riesgos de amenazas y peligros ambientales, así como el acceso no autorizado."),
    ("7.9", "Seguridad de los activos fuera de las instalaciones", "FIS",
     "Proteger los activos que se encuentran fuera de las instalaciones de la organización."),
    ("7.10", "Medios de almacenamiento", "FIS",
     "Gestionar los medios de almacenamiento a lo largo de su ciclo de vida: adquisición, uso, transporte y disposición, de acuerdo con el esquema de clasificación y los requisitos de manejo de la organización."),
    ("7.11", "Servicios de suministro", "FIS",
     "Proteger las instalaciones de procesamiento de información contra fallas de energía y otras interrupciones causadas por fallas en los servicios de suministro."),
    ("7.12", "Seguridad del cableado", "FIS",
     "Proteger el cableado de energía y telecomunicaciones que transporta datos o soporta servicios de información contra interceptación, interferencia o daño."),
    ("7.13", "Mantenimiento de equipos", "FIS",
     "Mantener correctamente los equipos para asegurar la disponibilidad, integridad y confidencialidad de la información."),
    ("7.14", "Eliminación o reutilización segura de equipos", "FIS",
     "Verificar que todo elemento de un equipo que contenga medios de almacenamiento haya sido revisado antes de su eliminación o reutilización, para asegurar que los datos sensibles y el software licenciado hayan sido eliminados o sobrescritos de forma segura."),
    # Tecnologicos
    ("8.1", "Dispositivos terminales de usuario", "TEC",
     "Proteger la información almacenada, procesada o accesible a través de los dispositivos terminales de usuario."),
    ("8.2", "Derechos de acceso privilegiado", "TEC",
     "Restringir y gestionar la asignación y uso de los derechos de acceso privilegiado."),
    ("8.3", "Restricción de acceso a la información", "TEC",
     "Restringir el acceso a la información y otros activos asociados de acuerdo con la política de control de acceso definida por la organización."),
    ("8.4", "Acceso al código fuente", "TEC",
     "Gestionar adecuadamente el acceso de lectura y escritura al código fuente, las herramientas de desarrollo y las bibliotecas de software."),
    ("8.5", "Autenticación segura", "TEC",
     "Implementar tecnologías y procedimientos de autenticación segura basados en las restricciones de acceso a la información y en la política de control de acceso."),
    ("8.6", "Gestión de capacidad", "TEC",
     "Monitorear y ajustar el uso de recursos, así como proyectar los requisitos de capacidad futura, para asegurar el desempeño requerido del sistema."),
    ("8.7", "Protección contra malware", "TEC",
     "Implementar controles de protección contra malware, complementados con la concienciación adecuada del usuario."),
    ("8.8", "Gestión de vulnerabilidades técnicas", "TEC",
     "Obtener información sobre las vulnerabilidades técnicas de los sistemas en uso, evaluar la exposición de la organización a ellas y tomar las medidas adecuadas."),
    ("8.9", "Gestión de la configuración", "TEC",
     "Establecer, documentar, implementar, monitorear y revisar configuraciones seguras de hardware, software, servicios y redes."),
    ("8.10", "Eliminación de información", "TEC",
     "Eliminar la información almacenada en sistemas, dispositivos o en cualquier otro medio de almacenamiento cuando ya no sea requerida."),
    ("8.11", "Enmascaramiento de datos", "TEC",
     "Utilizar enmascaramiento de datos de acuerdo con la política de control de acceso de la organización y otros requisitos relacionados, considerando la legislación aplicable."),
    ("8.12", "Prevención de fuga de datos", "TEC",
     "Aplicar medidas de prevención de fuga de datos a los sistemas, redes y otros dispositivos que procesan, almacenan o transmiten información sensible."),
    ("8.13", "Copias de seguridad de la información", "TEC",
     "Mantener y probar periódicamente copias de seguridad de la información, el software y los sistemas, de acuerdo con la política de copias de seguridad acordada."),
    ("8.14", "Redundancia de los recursos de tratamiento de información", "TEC",
     "Implementar recursos de procesamiento de información con suficiente redundancia para cumplir con los requisitos de disponibilidad."),
    ("8.15", "Registro de eventos (logging)", "TEC",
     "Generar, almacenar, proteger y analizar registros (logs) que documenten actividades, excepciones, fallas y otros eventos relevantes."),
    ("8.16", "Actividades de monitoreo", "TEC",
     "Monitorear las redes, sistemas y aplicaciones en busca de comportamiento anómalo, y tomar acciones adecuadas para evaluar posibles incidentes de seguridad de la información."),
    ("8.17", "Sincronización de relojes", "TEC",
     "Sincronizar los relojes de los sistemas de procesamiento de información utilizados por la organización con fuentes de tiempo aprobadas."),
    ("8.18", "Uso de programas de utilidad privilegiados", "TEC",
     "Restringir y controlar estrictamente el uso de programas de utilidad que puedan anular los controles del sistema y de las aplicaciones."),
    ("8.19", "Instalación de software en sistemas operativos", "TEC",
     "Establecer e implementar procedimientos y medidas para gestionar de forma segura la instalación de software en sistemas operativos."),
    ("8.20", "Seguridad de las redes", "TEC",
     "Asegurar, gestionar y controlar las redes y los dispositivos de red para proteger la información en sistemas y aplicaciones."),
    ("8.21", "Seguridad de los servicios de red", "TEC",
     "Identificar, implementar y monitorear los mecanismos de seguridad, los niveles de servicio y los requisitos de gestión de los servicios de red."),
    ("8.22", "Segregación de redes", "TEC",
     "Segregar en la red los grupos de servicios de información, usuarios y sistemas de información."),
    ("8.23", "Filtrado web", "TEC",
     "Gestionar el acceso a sitios web externos para reducir la exposición a contenido malicioso."),
    ("8.24", "Uso de criptografía", "TEC",
     "Definir e implementar reglas para el uso efectivo de la criptografía, incluyendo la gestión de claves criptográficas."),
    ("8.25", "Ciclo de vida de desarrollo seguro", "TEC",
     "Establecer y aplicar reglas para el desarrollo seguro de software y sistemas."),
    ("8.26", "Requisitos de seguridad de las aplicaciones", "TEC",
     "Identificar, especificar y aprobar los requisitos de seguridad de la información al desarrollar o adquirir aplicaciones."),
    ("8.27", "Principios de arquitectura e ingeniería de sistemas seguros", "TEC",
     "Establecer, documentar, mantener y aplicar principios de ingeniería de sistemas seguros a las actividades de desarrollo de sistemas de información."),
    ("8.28", "Codificación segura", "TEC",
     "Aplicar principios de codificación segura al desarrollo de software."),
    ("8.29", "Pruebas de seguridad en el desarrollo y aceptación", "TEC",
     "Definir e implementar procesos de prueba de seguridad en el ciclo de vida del desarrollo."),
    ("8.30", "Desarrollo externalizado", "TEC",
     "Dirigir, monitorear y revisar las actividades relacionadas con el desarrollo de sistemas subcontratado a terceros."),
    ("8.31", "Separación de los entornos de desarrollo, prueba y producción", "TEC",
     "Separar y asegurar los entornos de desarrollo, prueba y producción."),
    ("8.32", "Gestión de cambios", "TEC",
     "Someter los cambios en las instalaciones y sistemas de procesamiento de información a procedimientos de gestión de cambios."),
    ("8.33", "Información de prueba", "TEC",
     "Seleccionar, proteger y gestionar adecuadamente la información utilizada en las pruebas."),
    ("8.34", "Protección de los sistemas de información durante las pruebas de auditoría", "TEC",
     "Planificar y acordar entre el equipo de auditoría y el personal responsable las pruebas de auditoría y otras actividades de aseguramiento que involucren la evaluación de sistemas operativos."),
]

# Periodicidad sugerida (en meses) de revisión para los controles cuya
# naturaleza es de revisión recurrente, no de "cumple/no cumple" una sola
# vez. ISO/IEC 27002:2022 no fija una frecuencia exacta para estos
# controles: cada organización debe definir la suya en su propio programa
# de revisiones. Estos son valores de partida razonables (criterio propio),
# pensados para ajustarse más adelante control por control o por cliente.
PERIODICIDAD_REVISION = {
    "5.1": 12,   # Políticas de seguridad de la información
    "5.7": 6,    # Inteligencia de amenazas
    "5.9": 12,   # Inventario de información y otros activos asociados
    "5.19": 12,  # Seguridad de la información en las relaciones con proveedores
    "5.22": 12,  # Seguimiento, revisión y gestión de cambios de servicios de proveedores
    "5.31": 12,  # Requisitos legales, estatutarios, reglamentarios y contractuales
    "5.35": 12,  # Revisión independiente de la seguridad de la información
    "5.36": 12,  # Cumplimiento de políticas, reglas y normas de seguridad
    "6.3": 12,   # Concienciación, educación y capacitación en seguridad
    "8.8": 3,    # Gestión de vulnerabilidades técnicas
    "8.9": 6,    # Gestión de la configuración
}


class Command(BaseCommand):
    help = "Carga o actualiza el catálogo de controles ISO/IEC 27002:2022 en la base de datos."

    def handle(self, *args, **options):
        creados, actualizados = 0, 0
        for codigo, nombre, tema, descripcion in CONTROLES:
            _, created = Control.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "tema": tema,
                    "descripcion": descripcion,
                    "periodicidad_revision_meses": PERIODICIDAD_REVISION.get(codigo),
                },
            )
            creados += created
            actualizados += not created

        self.stdout.write(self.style.SUCCESS(
            f"Controles cargados: {creados} creados, {actualizados} actualizados. Total en catálogo: {len(CONTROLES)}."
        ))
