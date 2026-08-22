"""Generate professional Compliance Package (project-aware)"""
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime


class ComplianceGenerator:
    @staticmethod
    def generate(project=None, requirements=None):
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates'
        )
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('compliance.html')

        project_name = "Application"
        project_id = "PROJ-0001"
        domain = "general"
        has_payment = False

        if project:
            project_name = project.name if project.name and not project.name.startswith('Project_') else \
                           (project.raw_input[:60].strip() if project.raw_input else project.name)
            project_id = project.project_id
            domain = project.domain or 'general'
            raw = (project.raw_input or '').lower()
            has_payment = any(w in raw for w in ['payment', 'pay', 'checkout', 'card', 'stripe', 'razorpay'])

        html = template.render(
            title="Compliance Package",
            subtitle="Data Protection & Security Assessment",
            project_name=project_name,
            project_id=project_id,
            domain=domain,
            date=datetime.now().strftime("%Y-%m-%d"),
            has_payment=has_payment,
        )
        return html
