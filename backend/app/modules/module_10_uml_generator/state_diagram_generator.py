"""Generate State Diagrams from requirements and project description (domain-aware state machines)"""
import re
from typing import List, Dict, Any

# Domain-specific state machines
DOMAIN_STATE_MACHINES = {
    "food_delivery": {
        "Order": {
            "states": ["Placed", "Accepted", "Preparing", "ReadyForPickup", "PickedUp", "OutForDelivery", "Delivered", "Cancelled", "Refunded"],
            "transitions": [
                ("Placed", "Accepted", "Restaurant accepts"),
                ("Placed", "Cancelled", "Restaurant rejects / timeout"),
                ("Accepted", "Preparing", "Cooking started"),
                ("Preparing", "ReadyForPickup", "Food ready"),
                ("ReadyForPickup", "PickedUp", "Driver picks up"),
                ("PickedUp", "OutForDelivery", "En route"),
                ("OutForDelivery", "Delivered", "Customer received"),
                ("OutForDelivery", "Cancelled", "Delivery failed"),
                ("Delivered", "Refunded", "Customer dispute"),
                ("Accepted", "Cancelled", "Customer cancels"),
            ],
            "initial": "Placed",
            "final": ["Delivered", "Refunded", "Cancelled"],
        },
        "Payment": {
            "states": ["Pending", "Authorized", "Captured", "Failed", "Refunded", "Voided"],
            "transitions": [
                ("Pending", "Authorized", "Payment gateway approved"),
                ("Pending", "Failed", "Gateway declined"),
                ("Authorized", "Captured", "Order confirmed"),
                ("Authorized", "Voided", "Order cancelled before capture"),
                ("Captured", "Refunded", "Refund requested"),
                ("Failed", "Pending", "User retries"),
            ],
            "initial": "Pending",
            "final": ["Captured", "Refunded", "Voided"],
        },
    },
    "ecommerce": {
        "Order": {
            "states": ["Draft", "Placed", "Confirmed", "Processing", "Shipped", "OutForDelivery", "Delivered", "Returned", "Refunded", "Cancelled"],
            "transitions": [
                ("Draft", "Placed", "Customer submits"),
                ("Placed", "Confirmed", "Payment successful"),
                ("Placed", "Cancelled", "Payment failed"),
                ("Confirmed", "Processing", "Seller accepts"),
                ("Processing", "Shipped", "Item dispatched"),
                ("Shipped", "OutForDelivery", "In local facility"),
                ("OutForDelivery", "Delivered", "Delivery confirmed"),
                ("Delivered", "Returned", "Return requested"),
                ("Returned", "Refunded", "Return processed"),
                ("Confirmed", "Cancelled", "Customer cancels"),
            ],
            "initial": "Draft",
            "final": ["Delivered", "Refunded", "Cancelled"],
        },
    },
    "general": {
        "Request": {
            "states": ["New", "Pending", "InProgress", "Completed", "Failed", "Cancelled"],
            "transitions": [
                ("New", "Pending", "Submitted"),
                ("Pending", "InProgress", "Processing started"),
                ("InProgress", "Completed", "Successfully processed"),
                ("InProgress", "Failed", "Error occurred"),
                ("Failed", "Pending", "Retry"),
                ("Pending", "Cancelled", "Cancelled by user"),
            ],
            "initial": "New",
            "final": ["Completed", "Cancelled"],
        },
    },
}


class StateDiagramGenerator:
    """Domain-aware state machine diagram generator"""

    @classmethod
    def generate(cls, requirements: List[Dict], raw_input: str = "", domain: str = "general") -> Dict[str, Any]:
        """Generate PlantUML state diagram with domain-specific state machines"""
        combined = raw_input + " " + " ".join(r.get("text", "") for r in requirements)
        detected_domain = cls._detect_domain(combined.lower(), domain)

        state_machines = DOMAIN_STATE_MACHINES.get(detected_domain, DOMAIN_STATE_MACHINES["general"])

        plantuml = [
            "@startuml",
            "skinparam state {",
            "  BackgroundColor LightBlue",
            "  BorderColor DarkBlue",
            "  ArrowColor Navy",
            "}",
            "skinparam stateFontSize 12",
            "",
        ]

        for entity_name, sm in state_machines.items():
            plantuml.append(f"state \"{entity_name} State Machine\" as {entity_name} {{")
            plantuml.append(f"  [*] --> {sm['initial']}")
            plantuml.append("")
            for state in sm["states"]:
                if state in sm.get("final", []):
                    plantuml.append(f"  state \"{state}\" as {state} #LightGreen")
                else:
                    plantuml.append(f"  state \"{state}\" as {state}")
            plantuml.append("")
            for from_s, to_s, label in sm["transitions"]:
                plantuml.append(f"  {from_s} --> {to_s} : {label}")
            for final_state in sm.get("final", []):
                plantuml.append(f"  {final_state} --> [*]")
            plantuml.append("}")
            plantuml.append("")

        plantuml.append("@enduml")

        return {
            "plantuml": "\n".join(plantuml),
            "states": state_machines,
            "domain": detected_domain,
        }

    @classmethod
    def _detect_domain(cls, text: str, hint: str) -> str:
        if hint and hint != "general" and hint in DOMAIN_STATE_MACHINES:
            return hint
        if any(w in text for w in ["food", "delivery", "restaurant"]):
            return "food_delivery"
        if any(w in text for w in ["shop", "ecommerce", "product", "cart"]):
            return "ecommerce"
        return "general"