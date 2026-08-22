"""Generate Sequence diagrams from requirements and project description (domain-aware workflows)"""
import re
from typing import List, Dict, Any

# Domain-specific sequence flows
DOMAIN_FLOWS = {
    "food_delivery": {
        "order_placement": {
            "participants": ["Customer", "MobileApp", "APIGateway", "OrderService", "RestaurantService", "PaymentGateway", "NotificationService"],
            "messages": [
                ("Customer", "MobileApp", "Browse restaurants"),
                ("MobileApp", "APIGateway", "GET /restaurants"),
                ("APIGateway", "RestaurantService", "fetchNearby(location)"),
                ("RestaurantService", "MobileApp", "return restaurantList"),
                ("Customer", "MobileApp", "Select items & place order"),
                ("MobileApp", "APIGateway", "POST /orders"),
                ("APIGateway", "OrderService", "createOrder(items, address)"),
                ("OrderService", "PaymentGateway", "processPayment(amount)"),
                ("PaymentGateway", "OrderService", "paymentConfirmed"),
                ("OrderService", "RestaurantService", "notifyRestaurant(orderId)"),
                ("OrderService", "NotificationService", "sendConfirmation(customerId)"),
                ("NotificationService", "Customer", "Order Confirmation SMS/Push"),
                ("RestaurantService", "MobileApp", "orderStatus: Preparing"),
            ],
        },
        "delivery_tracking": {
            "participants": ["Customer", "MobileApp", "TrackingService", "DeliveryDriver", "DriverApp"],
            "messages": [
                ("DeliveryDriver", "DriverApp", "Accept delivery"),
                ("DriverApp", "TrackingService", "updateLocation(lat, lng)"),
                ("TrackingService", "MobileApp", "push: driverLocation"),
                ("MobileApp", "Customer", "Show real-time tracking"),
                ("DeliveryDriver", "DriverApp", "Mark as Delivered"),
                ("DriverApp", "TrackingService", "orderStatus: Delivered"),
                ("TrackingService", "MobileApp", "push: orderDelivered"),
                ("MobileApp", "Customer", "Request Rating"),
            ],
        },
    },
    "ecommerce": {
        "checkout": {
            "participants": ["Customer", "WebApp", "APIGateway", "OrderService", "PaymentGateway", "InventoryService", "EmailService"],
            "messages": [
                ("Customer", "WebApp", "Add to cart"),
                ("WebApp", "APIGateway", "POST /cart/items"),
                ("Customer", "WebApp", "Proceed to checkout"),
                ("WebApp", "APIGateway", "GET /cart/{cartId}"),
                ("APIGateway", "InventoryService", "checkStock(items)"),
                ("InventoryService", "APIGateway", "stockAvailable: true"),
                ("Customer", "WebApp", "Enter payment details"),
                ("WebApp", "APIGateway", "POST /orders"),
                ("APIGateway", "OrderService", "createOrder(cart, address)"),
                ("OrderService", "PaymentGateway", "chargeCard(amount)"),
                ("PaymentGateway", "OrderService", "paymentSuccess"),
                ("OrderService", "InventoryService", "reduceStock(items)"),
                ("OrderService", "EmailService", "sendOrderConfirmation(email)"),
                ("EmailService", "Customer", "Order confirmation email"),
            ],
        },
    },
    "healthcare": {
        "appointment_booking": {
            "participants": ["Patient", "HealthPortal", "AppointmentService", "DoctorService", "NotificationService"],
            "messages": [
                ("Patient", "HealthPortal", "Search for doctor"),
                ("HealthPortal", "DoctorService", "getDoctors(specialization)"),
                ("DoctorService", "HealthPortal", "return doctorList"),
                ("Patient", "HealthPortal", "Select doctor & slot"),
                ("HealthPortal", "AppointmentService", "bookAppointment(doctorId, slot)"),
                ("AppointmentService", "DoctorService", "checkAvailability(slot)"),
                ("DoctorService", "AppointmentService", "slotAvailable: true"),
                ("AppointmentService", "NotificationService", "sendConfirmation(patientId, doctorId)"),
                ("NotificationService", "Patient", "Appointment confirmation"),
            ],
        },
    },
    "general": {
        "login": {
            "participants": ["User", "WebApp", "AuthService", "Database", "NotificationService"],
            "messages": [
                ("User", "WebApp", "Enter credentials"),
                ("WebApp", "AuthService", "POST /auth/login"),
                ("AuthService", "Database", "validateUser(email, password)"),
                ("Database", "AuthService", "userRecord"),
                ("AuthService", "WebApp", "JWT token"),
                ("WebApp", "User", "Redirect to dashboard"),
                ("AuthService", "NotificationService", "logLoginActivity()"),
            ],
        },
    },
}


class SequenceGenerator:
    """Domain-aware sequence diagram generator with realistic multi-participant flows"""

    @classmethod
    def generate(cls, requirements: List[Dict], raw_input: str = "", domain: str = "general") -> Dict[str, Any]:
        """Generate PlantUML sequence diagram with domain-specific workflows"""
        combined = raw_input + " " + " ".join(r.get("text", "") for r in requirements)
        detected_domain = cls._detect_domain(combined.lower(), domain)

        # Pick the most relevant flow for this domain
        domain_flows = DOMAIN_FLOWS.get(detected_domain, DOMAIN_FLOWS["general"])
        flow_key = cls._pick_best_flow(combined.lower(), list(domain_flows.keys()))
        flow = domain_flows[flow_key]

        participants = flow["participants"]
        messages = flow["messages"]

        plantuml = ["@startuml",
                    "skinparam sequenceArrowThickness 2",
                    "skinparam roundcorner 8",
                    "skinparam sequenceParticipant {",
                    "  BackgroundColor #E8F4FD",
                    "  BorderColor #2980B9",
                    "}",
                    "skinparam sequenceMessageAlign center",
                    "autonumber", ""]

        for p in participants:
            clean_p = re.sub(r"\W+", "", p)
            if any(svc in p for svc in ["Service", "Gateway", "API"]):
                plantuml.append(f'participant "{p}" as {clean_p} #LightGreen')
            elif p in ["Database", "DB"]:
                plantuml.append(f'database "{p}" as {clean_p}')
            else:
                plantuml.append(f'actor "{p}" as {clean_p}')

        plantuml.append("")
        for sender, receiver, message in messages:
            s = re.sub(r'\W+', '', sender)
            r = re.sub(r'\W+', '', receiver)
            plantuml.append(f"{s} -> {r} : {message}")

        plantuml.append("@enduml")

        return {
            "plantuml": "\n".join(plantuml),
            "participants": participants,
            "messages": messages,
            "flow_type": flow_key,
            "domain": detected_domain,
        }

    @classmethod
    def _detect_domain(cls, text: str, hint: str) -> str:
        if hint and hint != "general" and hint in DOMAIN_FLOWS:
            return hint
        if any(w in text for w in ["food", "delivery", "restaurant", "meal"]):
            return "food_delivery"
        if any(w in text for w in ["shop", "cart", "ecommerce", "product"]):
            return "ecommerce"
        if any(w in text for w in ["patient", "doctor", "appointment"]):
            return "healthcare"
        return "general"

    @classmethod
    def _pick_best_flow(cls, text: str, flow_keys: List[str]) -> str:
        """Choose the most relevant flow based on text keywords"""
        if "track" in text or "delivery" in text:
            for k in flow_keys:
                if "track" in k or "delivery" in k:
                    return k
        if "checkout" in text or "payment" in text:
            for k in flow_keys:
                if "checkout" in k or "order" in k:
                    return k
        return flow_keys[0]