"""Generate Use Case diagrams from requirements and project raw_input (domain-aware)"""
import re
from typing import List, Dict, Set, Any


# Domain-specific actor & use case knowledge base
DOMAIN_ACTORS = {
    "food_delivery": ["Customer", "Restaurant", "DeliveryDriver", "Admin", "PaymentGateway"],
    "ecommerce": ["Customer", "Seller", "Admin", "PaymentGateway", "ShippingService"],
    "healthcare": ["Patient", "Doctor", "Nurse", "Admin", "Pharmacist", "InsuranceProvider"],
    "banking": ["Customer", "Teller", "Manager", "Admin", "ExternalBank"],
    "education": ["Student", "Teacher", "Admin", "Parent", "ExamBoard"],
    "travel": ["Traveler", "Agent", "Airline", "Hotel", "PaymentGateway"],
    "social_media": ["User", "Admin", "Advertiser", "Moderator"],
    "general": ["User", "Admin", "System"],
}

DOMAIN_USE_CASES = {
    "food_delivery": [
        ("Customer", ["Browse Menu", "Place Order", "Track Delivery", "Make Payment", "Rate Order", "Apply Coupon", "Manage Profile"]),
        ("Restaurant", ["Manage Menu", "Accept Order", "Update Order Status", "View Analytics"]),
        ("DeliveryDriver", ["Accept Delivery", "Update Location", "Mark Delivered", "View Earnings"]),
        ("Admin", ["Manage Users", "Manage Restaurants", "View Reports", "Handle Disputes"]),
    ],
    "ecommerce": [
        ("Customer", ["Browse Products", "Search Items", "Add to Cart", "Checkout", "Track Order", "Return Product", "Write Review"]),
        ("Seller", ["List Product", "Manage Inventory", "Process Order", "View Sales"]),
        ("Admin", ["Manage Users", "Manage Products", "Handle Disputes", "View Analytics"]),
    ],
    "healthcare": [
        ("Patient", ["Book Appointment", "View Records", "Make Payment", "Request Prescription"]),
        ("Doctor", ["View Patient Records", "Write Prescription", "Manage Schedule", "Issue Referral"]),
        ("Admin", ["Manage Appointments", "Manage Staff", "Generate Reports", "Handle Billing"]),
    ],
    "general": [
        ("User", ["Login", "Register", "View Dashboard", "Update Profile", "Logout"]),
        ("Admin", ["Manage Users", "View Reports", "Configure System"]),
    ],
}


class UseCaseGenerator:
    """Domain-aware use case diagram generator"""

    @classmethod
    def generate(cls, requirements: List[Dict], raw_input: str = "", domain: str = "general") -> Dict[str, Any]:
        """
        Generate PlantUML use case diagram.
        Uses domain knowledge base + requirement text mining.
        """
        combined_text = raw_input + " " + " ".join([r.get("text", "") for r in requirements])
        text_lower = combined_text.lower()

        # Detect domain from text
        detected_domain = cls._detect_domain(text_lower, domain)

        # Get base actors and use cases from knowledge base
        base_actors = DOMAIN_ACTORS.get(detected_domain, DOMAIN_ACTORS["general"])
        base_use_cases = DOMAIN_USE_CASES.get(detected_domain, DOMAIN_USE_CASES["general"])

        # Extract additional use cases from requirement texts
        extra_uc = cls._extract_from_requirements(requirements, raw_input)

        # Build PlantUML
        plantuml = ["@startuml", "left to right direction", "skinparam packageStyle rect",
                    "skinparam usecase {", "  BackgroundColor LightBlue", "  BorderColor DarkBlue",
                    "  ArrowColor Navy", "}", ""]

        for actor in base_actors:
            sanitized = re.sub(r'\W+', '', actor)
            plantuml.append(f'actor "{actor}" as {sanitized}')
        plantuml.append("")

        plantuml.append('rectangle "System" {')

        all_uc_aliases = []
        for actor, use_cases in base_use_cases:
            for uc in use_cases:
                alias = re.sub(r'\W+', '', uc)[:20]
                plantuml.append(f'  usecase "{uc}" as {alias}')
                all_uc_aliases.append((actor, alias))

        # Add requirement-mined use cases
        for uc in extra_uc[:6]:
            alias = re.sub(r'\W+', '', uc)[:20]
            plantuml.append(f'  usecase "{uc}" as {alias}')
            all_uc_aliases.append(("User", alias))

        plantuml.append("}")
        plantuml.append("")

        # Relationships
        for actor, alias in all_uc_aliases:
            sanitized_actor = re.sub(r'\W+', '', actor)
            if sanitized_actor in [re.sub(r'\W+', '', a) for a in base_actors]:
                plantuml.append(f'{sanitized_actor} --> {alias}')

        plantuml.append("@enduml")

        return {
            "plantuml": "\n".join(plantuml),
            "actors": base_actors,
            "use_cases": [uc for _, ucs in base_use_cases for uc in ucs],
            "domain": detected_domain,
        }

    @classmethod
    def _detect_domain(cls, text: str, hint: str) -> str:
        if hint and hint != "general" and hint in DOMAIN_ACTORS:
            return hint
        if any(w in text for w in ["food", "delivery", "restaurant", "meal", "order food"]):
            return "food_delivery"
        if any(w in text for w in ["shop", "cart", "product", "ecommerce", "sell"]):
            return "ecommerce"
        if any(w in text for w in ["patient", "doctor", "hospital", "prescription"]):
            return "healthcare"
        if any(w in text for w in ["bank", "account", "transaction", "loan"]):
            return "banking"
        if any(w in text for w in ["student", "course", "teacher", "learning"]):
            return "education"
        if any(w in text for w in ["flight", "hotel", "travel", "booking"]):
            return "travel"
        return "general"

    @classmethod
    def _extract_from_requirements(cls, requirements: List[Dict], raw_input: str) -> List[str]:
        """Mine additional use cases from requirement verbs"""
        verb_pattern = re.compile(
            r'\b(login|register|search|filter|order|pay|track|view|edit|delete|upload|download|'
            r'generate|export|import|approve|reject|cancel|confirm|send|receive|notify|report|'
            r'analyze|validate|browse|rate|review|schedule|book|reserve|subscribe|manage)\b',
            re.IGNORECASE
        )
        uc_set = set()
        for req in requirements:
            text = req.get("text", "")
            for match in verb_pattern.finditer(text):
                verb = match.group(0)
                words = text.split()
                try:
                    idx = next(i for i, w in enumerate(words) if verb.lower() in w.lower())
                    if idx + 1 < len(words):
                        noun = re.sub(r'\W+', '', words[idx + 1])
                        if len(noun) > 2 and noun.lower() not in {"the", "a", "an", "to", "of", "for", "and"}:
                            uc_set.add(f"{verb.capitalize()} {noun.capitalize()}")
                except StopIteration:
                    pass
        return list(uc_set)