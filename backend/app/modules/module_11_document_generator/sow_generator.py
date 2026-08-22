"""Generate SOW document from project data (with full context)"""
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime


class SOWGenerator:
    @staticmethod
    def generate(project, impact_details, requirements):
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates'
        )
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('sow.html')

        effort_hours = impact_details.get('total_effort_hours', 0) or 0
        # Estimate timeline: total hours / 40 hours/week / 2 developers
        total_weeks = max(8, round(effort_hours / 80)) if effort_hours > 0 else 12

        milestones = [
            {"name": "Project Kickoff & Requirements Finalization", "week": 1, "deliverables": "Approved SRS, Project Plan, Kickoff Meeting"},
            {"name": "Architecture & System Design", "week": 2, "deliverables": "UML Diagrams (7 types), DB Schema, Architecture Document"},
            {"name": "Backend Development (MVP)", "week": max(3, total_weeks // 2), "deliverables": "Core APIs, Business Logic, Database Integration"},
            {"name": "Frontend Development", "week": max(4, total_weeks // 2 + 2), "deliverables": "UI Implementation, API Integration, Responsive Design"},
            {"name": "Testing & QA", "week": total_weeks - 2, "deliverables": "Test Reports, Bug Fixes, Performance Validation"},
            {"name": "UAT & Client Review", "week": total_weeks - 1, "deliverables": "UAT Sign-off, Final Bug Fixes"},
            {"name": "Production Deployment & Go-live", "week": total_weeks, "deliverables": "Live System, Deployment Documentation, Handover"},
        ]

        hourly_rate = 100
        budget_estimate = round(effort_hours * hourly_rate) if effort_hours > 0 else 50000

        # Extract feature areas from requirements
        features = list(set([r.category for r in requirements if r.category and r.category != 'General']))[:6]
        if not features:
            # Generate from raw_input keywords
            raw = (project.raw_input or '').lower()
            if 'track' in raw: features.append('Real-time Tracking')
            if 'payment' in raw or 'pay' in raw: features.append('Payment Processing')
            if 'notification' in raw or 'notify' in raw: features.append('Push Notifications')
            if 'auth' in raw or 'login' in raw: features.append('User Authentication & Authorization')
            if 'report' in raw or 'analytics' in raw: features.append('Analytics & Reporting')
            if not features:
                features = ['Core Business Logic', 'User Management', 'Data Management', 'API Development']

        # Integrations
        integrations = []
        all_text = (project.raw_input or '').lower()
        if any(w in all_text for w in ['payment', 'pay', 'checkout']): integrations.append('Payment Gateway')
        if any(w in all_text for w in ['map', 'location', 'gps']): integrations.append('Maps API')
        if any(w in all_text for w in ['email', 'sms', 'notification']): integrations.append('Notification Service')
        if not integrations: integrations = ['Email Service', 'Cloud Storage']

        # Project name
        project_name = project.name if project.name and not project.name.startswith('Project_') else \
                       (project.raw_input[:60].strip() if project.raw_input else project.name)

        html = template.render(
            title="Statement of Work (SOW)",
            subtitle="Project Contract Document",
            project_name=project_name,
            project_id=project.project_id,
            domain=project.domain or 'general',
            date=datetime.now().strftime("%Y-%m-%d"),
            objective=f"Develop and deliver a production-ready {project.domain or 'software'} system: {project.raw_input[:200] if project.raw_input else 'as defined in the SRS document'}.",
            features=features,
            integrations=integrations,
            milestones=milestones,
            total_weeks=total_weeks,
            total_effort_hours=effort_hours,
            budget_estimate=budget_estimate,
            hourly_rate=hourly_rate,
        )
        return html
