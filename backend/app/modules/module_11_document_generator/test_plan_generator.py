"""Generate IEEE 829-compliant Test Plan from requirements (with full project context)"""
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime


class TestPlanGenerator:
    @staticmethod
    def generate(requirements, project=None):
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates'
        )
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('test_plan.html')

        project_name = ""
        project_id = ""
        if project:
            project_name = project.name if project.name and not project.name.startswith('Project_') else \
                           (project.raw_input[:60].strip() if project.raw_input else project.name)
            project_id = project.project_id

        test_cases = []
        for idx, req in enumerate(requirements[:100]):
            test_id = f"TC-{idx + 1:03d}"
            req_text = req.text or ''
            req_id = req.requirement_id or req.id or f"REQ-{idx + 1:03d}"

            # Generate meaningful test case descriptions based on requirement text
            desc = f"Verify that: {req_text[:250]}"
            if 'user' in req_text.lower() or 'login' in req_text.lower():
                preconditions = "Test user account exists and is active; system is accessible"
            elif 'payment' in req_text.lower():
                preconditions = "Test payment gateway sandbox configured; test card credentials available"
            elif 'database' in req_text.lower() or 'store' in req_text.lower():
                preconditions = "Test database is populated with seed data; application running"
            else:
                preconditions = "System is operational; test environment configured"

            # Expected result based on requirement type
            if any(w in req_text.lower() for w in ['shall', 'must', 'should', 'will']):
                expected = f"System successfully fulfills: '{req_text[:120]}'. Response code 200; no errors."
            else:
                expected = "System behaves as specified in the requirement with no errors or exceptions."

            test_cases.append({
                "id": test_id,
                "req_id": req_id,
                "description": desc,
                "preconditions": preconditions,
                "expected": expected,
            })

        html = template.render(
            title="Test Plan",
            subtitle="IEEE 829 Standard",
            project_name=project_name,
            project_id=project_id,
            date=datetime.now().strftime("%Y-%m-%d"),
            test_cases=test_cases,
        )
        return html
