"""Generate IEEE 830 SRS document from project data (with full context)"""
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime


class SRSGenerator:
    @staticmethod
    def generate(project, requirements, conflicts, impact_details, quality_details, diagrams=None):
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'templates'
        )
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('srs.html')

        # Separate requirements by type
        functional = [r for r in requirements if r.type and r.type.value in ('functional',)]
        nonfunctional = [r for r in requirements if r.type and r.type.value in ('non_functional', 'constraint', 'non-functional')]

        # Extract actors from requirement texts
        actors = set()
        for req in requirements:
            text_lower = (req.text or '').lower()
            if 'user' in text_lower: actors.add('User')
            if 'admin' in text_lower or 'administrator' in text_lower: actors.add('Admin')
            if 'customer' in text_lower: actors.add('Customer')
            if 'driver' in text_lower: actors.add('Delivery Driver')
            if 'restaurant' in text_lower: actors.add('Restaurant')
            if 'manager' in text_lower: actors.add('Manager')
        actors = sorted(actors) if actors else ['End User', 'Administrator']

        # Detect integrations from raw_input and requirements
        all_text = (project.raw_input or '') + ' '.join(r.text for r in requirements)
        integrations = []
        if any(w in all_text.lower() for w in ['payment', 'pay', 'checkout', 'stripe', 'razorpay']):
            integrations.append('Payment Gateway (Stripe / Razorpay)')
        if any(w in all_text.lower() for w in ['map', 'location', 'gps', 'track']):
            integrations.append('Maps API (Google Maps / MapBox)')
        if any(w in all_text.lower() for w in ['email', 'notification', 'sms', 'push']):
            integrations.append('Notification Service (Firebase / Twilio)')
        if any(w in all_text.lower() for w in ['social', 'google', 'facebook', 'oauth']):
            integrations.append('OAuth 2.0 / Social Login Provider')
        if not integrations:
            integrations = ['Email Notification Service', 'Cloud Storage', 'External Authentication']

        # Project name — prefer raw_input[:60] over generic "Project_X"
        project_name = project.name if project.name and not project.name.startswith('Project_') else \
                       (project.raw_input[:60].strip() if project.raw_input else project.name)

        html = template.render(
            title="Software Requirements Specification (SRS)",
            subtitle="IEEE 830 Standard",
            project_name=project_name,
            project_id=project.project_id,
            domain=project.domain or 'general',
            date=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
            scope_summary=project.raw_input[:200] if project.raw_input else f"{project.domain} system with {len(requirements)} requirements",
            integrations=integrations,
            actors=actors,
            functional_requirements=functional if functional else requirements,
            nonfunctional_requirements=nonfunctional,
            conflicts=conflicts,
            total_effort_hours=impact_details.get('total_effort_hours', 0),
            total_person_days=impact_details.get('total_person_days', 0),
            max_complexity=impact_details.get('max_complexity', 1),
            high_risk_count=impact_details.get('high_risk_count', 0),
            avg_rqi=round(quality_details.get('average_rqi', 0), 1),
            rating=quality_details.get('rating', 'Fair'),
            has_payment=any(w in (project.raw_input or '').lower() for w in ['payment', 'pay', 'checkout']),
        )
        return html
