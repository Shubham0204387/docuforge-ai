"""Generate professional Deployment Guide (project-aware)"""
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime


class DeploymentGuideGenerator:
    @staticmethod
    def generate(project=None):
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates'
        )
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('deployment.html')

        project_name = "Application"
        project_id = "PROJ-0001"
        domain = "general"

        if project:
            project_name = project.name if project.name and not project.name.startswith('Project_') else \
                           (project.raw_input[:60].strip() if project.raw_input else project.name)
            project_id = project.project_id
            domain = project.domain or 'general'

        html = template.render(
            title="Production Deployment Guide",
            subtitle="Infrastructure & Operations",
            project_name=project_name,
            project_id=project_id,
            domain=domain,
            date=datetime.now().strftime("%Y-%m-%d"),
        )
        return html
