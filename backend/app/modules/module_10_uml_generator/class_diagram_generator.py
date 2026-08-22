"""Generate Class diagrams from requirements and project description (domain-aware entity extraction)"""
import re
from typing import List, Dict, Set, Any

# Domain entity knowledge base
DOMAIN_ENTITIES = {
    "food_delivery": {
        "Customer": ["customerId: String", "name: String", "email: String", "phone: String", "address: String", "orderHistory: List"],
        "Order": ["orderId: String", "status: String", "totalAmount: Float", "placedAt: DateTime", "deliveredAt: DateTime"],
        "Restaurant": ["restaurantId: String", "name: String", "address: String", "rating: Float", "cuisineType: String", "isOpen: Boolean"],
        "MenuItem": ["itemId: String", "name: String", "description: String", "price: Float", "category: String", "isAvailable: Boolean"],
        "DeliveryDriver": ["driverId: String", "name: String", "phone: String", "licenseNumber: String", "currentLocation: Location", "rating: Float"],
        "Payment": ["paymentId: String", "method: String", "amount: Float", "status: String", "transactionId: String"],
        "Cart": ["cartId: String", "items: List", "totalItems: Integer", "subtotal: Float"],
        "Review": ["reviewId: String", "rating: Integer", "comment: String", "createdAt: DateTime"],
    },
    "ecommerce": {
        "Customer": ["customerId: String", "name: String", "email: String", "shippingAddress: Address"],
        "Product": ["productId: String", "name: String", "price: Float", "stock: Integer", "category: String", "images: List"],
        "Order": ["orderId: String", "status: String", "totalAmount: Float", "orderDate: DateTime"],
        "Cart": ["cartId: String", "items: List", "totalAmount: Float"],
        "Payment": ["paymentId: String", "method: String", "amount: Float", "status: String"],
        "Seller": ["sellerId: String", "businessName: String", "email: String", "rating: Float"],
        "Category": ["categoryId: String", "name: String", "parentCategory: String"],
    },
    "healthcare": {
        "Patient": ["patientId: String", "name: String", "dateOfBirth: Date", "medicalHistory: List", "insuranceId: String"],
        "Doctor": ["doctorId: String", "name: String", "specialization: String", "licenseNumber: String"],
        "Appointment": ["appointmentId: String", "dateTime: DateTime", "status: String", "reason: String"],
        "Prescription": ["prescriptionId: String", "medications: List", "dosage: String", "issuedDate: Date"],
        "MedicalRecord": ["recordId: String", "diagnosis: String", "treatment: String", "date: Date"],
    },
    "general": {
        "User": ["userId: String", "username: String", "email: String", "password: String", "role: String"],
        "Session": ["sessionId: String", "createdAt: DateTime", "expiresAt: DateTime"],
        "Notification": ["notificationId: String", "message: String", "isRead: Boolean", "createdAt: DateTime"],
    },
}

DOMAIN_RELATIONSHIPS = {
    "food_delivery": [
        ("Customer", "Order", "*", "1", "places"),
        ("Order", "Restaurant", "*", "1", "from"),
        ("Order", "MenuItem", "*", "*", "contains"),
        ("Order", "Payment", "1", "1", "has"),
        ("Order", "DeliveryDriver", "*", "1", "assignedTo"),
        ("Customer", "Cart", "1", "1", "has"),
        ("Cart", "MenuItem", "*", "*", "contains"),
        ("Customer", "Review", "1", "*", "writes"),
        ("Restaurant", "MenuItem", "1", "*", "offers"),
    ],
    "ecommerce": [
        ("Customer", "Order", "1", "*", "places"),
        ("Order", "Product", "*", "*", "contains"),
        ("Customer", "Cart", "1", "1", "has"),
        ("Cart", "Product", "*", "*", "contains"),
        ("Order", "Payment", "1", "1", "has"),
        ("Seller", "Product", "1", "*", "sells"),
        ("Product", "Category", "*", "1", "belongsTo"),
    ],
    "healthcare": [
        ("Patient", "Appointment", "1", "*", "books"),
        ("Doctor", "Appointment", "1", "*", "attends"),
        ("Doctor", "Prescription", "1", "*", "issues"),
        ("Patient", "MedicalRecord", "1", "*", "has"),
    ],
    "general": [
        ("User", "Session", "1", "*", "creates"),
        ("User", "Notification", "1", "*", "receives"),
    ],
}


class ClassDiagramGenerator:
    """Domain-aware class diagram generator with rich entity models"""

    @classmethod
    def generate(cls, requirements: List[Dict], raw_input: str = "", domain: str = "general") -> Dict[str, Any]:
        """Generate PlantUML class diagram with domain entities and relationships"""
        detected_domain = cls._detect_domain(raw_input + " " + " ".join(r.get("text", "") for r in requirements), domain)

        entities = DOMAIN_ENTITIES.get(detected_domain, DOMAIN_ENTITIES["general"])
        relationships = DOMAIN_RELATIONSHIPS.get(detected_domain, DOMAIN_RELATIONSHIPS["general"])

        plantuml = ["@startuml",
                    "skinparam classAttributeIconSize 0",
                    "skinparam classFontSize 12",
                    "skinparam class {",
                    "  BackgroundColor LightYellow",
                    "  BorderColor DarkOrange",
                    "  ArrowColor Navy",
                    "}", ""]

        for class_name, attributes in entities.items():
            plantuml.append(f"class {class_name} {{")
            for attr in attributes:
                plantuml.append(f"  + {attr}")
            plantuml.append("}")
            plantuml.append("")

        plantuml.append("")
        for rel in relationships:
            from_c, to_c, mult_from, mult_to, label = rel
            plantuml.append(f'{from_c} "{mult_from}" --> "{mult_to}" {to_c} : {label}')

        plantuml.append("@enduml")

        return {
            "plantuml": "\n".join(plantuml),
            "classes": list(entities.keys()),
            "attributes": entities,
            "relationships": relationships,
            "domain": detected_domain,
        }

    @classmethod
    def _detect_domain(cls, text: str, hint: str) -> str:
        text = text.lower()
        if hint and hint != "general" and hint in DOMAIN_ENTITIES:
            return hint
        if any(w in text for w in ["food", "delivery", "restaurant", "meal", "menu"]):
            return "food_delivery"
        if any(w in text for w in ["shop", "cart", "product", "ecommerce", "sell"]):
            return "ecommerce"
        if any(w in text for w in ["patient", "doctor", "hospital", "prescription", "appointment"]):
            return "healthcare"
        return "general"