# patient/management/commands/create_docx_template.py
from pathlib import Path

from django.core.management.base import BaseCommand

from docx import Document


class Command(BaseCommand):
    help = "Génère le template DOCX utilisé par docxtpl pour les observations médicales."

    def handle(self, *args, **options):
        app_dir = Path(__file__).resolve().parents[2]
        template_dir = app_dir / "docx_templates"
        template_dir.mkdir(parents=True, exist_ok=True)

        template_path = template_dir / "observation.docx"

        document = Document()

        document.add_heading("{{ title }}", 0)

        document.add_paragraph("{% for section in sections %}")

        document.add_heading("{{ section.title }}", level=1)

        document.add_paragraph("{% for block in section.blocks %}")

        document.add_paragraph("{% if block.title %}{{ block.title }}{% endif %}")

        document.add_paragraph("{% for line in block.lines %}")
        document.add_paragraph("{{ line }}")
        document.add_paragraph("{% endfor %}")

        document.add_paragraph("{% endfor %}")

        document.add_paragraph("{% endfor %}")

        document.save(template_path)

        self.stdout.write(
            self.style.SUCCESS(
                f"Template DOCX généré avec succès : {template_path}"
            )
        )