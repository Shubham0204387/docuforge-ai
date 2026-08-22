"""Generates contextual clarification questions based on vague terms and domain"""
from typing import List, Dict, Any, Optional
from backend.app.modules.module_2_clarification.vague_term_detector import VagueTermDetector

class QuestionGenerator:
    """Creates intelligent questions to refine requirements"""
    
    # Template questions for different vague term categories
    QUESTION_TEMPLATES = {
        "performance": [
            {
                "question": "What is the maximum acceptable response time for this operation?",
                "options": ["< 100ms", "< 500ms", "< 1 second", "< 2 seconds", "< 5 seconds"],
                "type": "multiple_choice",
                "clarifies": "response_time"
            },
            {
                "question": "How many concurrent users should the system support?",
                "options": ["< 100", "100-1000", "1000-10000", "10000-100000", "> 100000"],
                "type": "multiple_choice",
                "clarifies": "concurrent_users"
            }
        ],
        "time": [
            {
                "question": "How frequently should updates occur?",
                "options": ["Real-time (continuous)", "Every second", "Every 30 seconds", "Every minute", "Every 5 minutes"],
                "type": "multiple_choice",
                "clarifies": "update_frequency"
            },
            {
                "question": "What is the maximum acceptable delay for this operation?",
                "options": ["< 1 second", "< 5 seconds", "< 30 seconds", "< 1 minute", "< 5 minutes"],
                "type": "multiple_choice",
                "clarifies": "max_delay"
            }
        ],
        "security": [
            {
                "question": "What level of security compliance is required?",
                "options": ["Basic (password + HTTPS)", "Standard (2FA + encryption)", "Enterprise (SSO + HSM)", "Regulated (HIPAA/PCI/SOC2)"],
                "type": "multiple_choice",
                "clarifies": "security_level"
            },
            {
                "question": "Should data be encrypted at rest?",
                "options": ["Yes, all data", "Yes, sensitive data only", "No"],
                "type": "multiple_choice",
                "clarifies": "encryption_at_rest"
            }
        ],
        "scalability": [
            {
                "question": "What is the expected peak user load?",
                "options": ["< 100 users", "100-1000 users", "1000-10000 users", "10000-100000 users", "> 100000 users"],
                "type": "multiple_choice",
                "clarifies": "peak_users"
            },
            {
                "question": "What is the expected data growth per year?",
                "options": ["< 1 GB", "1-10 GB", "10-100 GB", "100 GB - 1 TB", "> 1 TB"],
                "type": "multiple_choice",
                "clarifies": "data_growth"
            }
        ],
        "quality": [
            {
                "question": "What is the required uptime / availability?",
                "options": ["99% (3.65 days downtime/year)", "99.9% (8.76 hours/year)", "99.99% (52 minutes/year)", "99.999% (5 minutes/year)"],
                "type": "multiple_choice",
                "clarifies": "uptime"
            }
        ],
        "domain_specific": {
            "ecommerce": [
                {
                    "question": "What payment methods should be supported?",
                    "options": ["Credit/Debit Cards", "Digital Wallets (PayPal, Google Pay)", "Cryptocurrency", "All of the above"],
                    "type": "multiple_choice",
                    "clarifies": "payment_methods"
                },
                {
                    "question": "Should the system support multiple currencies?",
                    "options": ["Single currency (USD)", "Multiple currencies (select which)", "Dynamic based on user location"],
                    "type": "multiple_choice",
                    "clarifies": "currencies"
                }
            ],
            "healthcare": [
                {
                    "question": "Which compliance regulations apply?",
                    "options": ["HIPAA", "GDPR", "PIPEDA", "None / Internal only"],
                    "type": "multiple_choice",
                    "clarifies": "compliance"
                }
            ],
            "finance": [
                {
                    "question": "What level of audit logging is required?",
                    "options": ["Basic (login/transaction logs)", "Detailed (all data access)", "Regulatory (immutable, 7+ years retention)"],
                    "type": "multiple_choice",
                    "clarifies": "audit_level"
                }
            ]
        }
    }
    
    @classmethod
    def generate_questions(cls, text: str, domain: str, vague_analysis: Dict) -> List[Dict]:
        """Generate questions based on vague terms and domain"""
        questions = []
        
        # Add questions for each detected vague category
        categories = vague_analysis.get("categories", {})
        for category, terms in categories.items():
            if terms and category in cls.QUESTION_TEMPLATES:
                templates = cls.QUESTION_TEMPLATES[category]
                # Add first relevant template for each category (avoid duplicates)
                for template in templates:
                    if template not in questions:
                        questions.append(template)
                        break
        
        # Add domain-specific questions
        if domain in cls.QUESTION_TEMPLATES.get("domain_specific", {}):
            domain_qs = cls.QUESTION_TEMPLATES["domain_specific"][domain]
            for q in domain_qs:
                if q not in questions:
                    questions.append(q)
        
        # If no questions generated, add default questions
        if not questions:
            questions = [
                {
                    "question": "What is the main goal of this project?",
                    "options": None,
                    "type": "text",
                    "clarifies": "goal"
                },
                {
                    "question": "Who are the primary users of this system?",
                    "options": None,
                    "type": "text",
                    "clarifies": "users"
                }
            ]
        
        # Limit to 5 questions per session (to avoid overwhelming)
        return questions[:5]
    
    @classmethod
    def generate_follow_up(cls, previous_answer: str, context: Dict) -> Optional[Dict]:
        """Generate a follow-up question based on previous answer"""
        # Simple follow-up logic - can be enhanced with NLP later
        answer_lower = previous_answer.lower()
        
        if "payment" in answer_lower and "methods" in context.get("last_question", ""):
            return {
                "question": "Do you need to store payment method information for future purchases?",
                "options": ["Yes", "No", "Only with user consent"],
                "type": "multiple_choice",
                "clarifies": "payment_storage"
            }
        
        if "real-time" in answer_lower or "every second" in answer_lower:
            return {
                "question": "Should the system continue updating when the app is in the background?",
                "options": ["Yes, always", "Yes, but with reduced frequency", "No"],
                "type": "multiple_choice",
                "clarifies": "background_updates"
            }
        
        return None
