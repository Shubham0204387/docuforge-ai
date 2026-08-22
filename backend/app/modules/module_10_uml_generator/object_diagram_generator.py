"""Generate Object Diagrams (instance-level snapshots) with realistic domain-specific sample data"""
from typing import List, Dict, Any
import re

DOMAIN_OBJECT_DIAGRAMS = {
    "food_delivery": """@startuml
skinparam object {
  BackgroundColor #FDEBD0
  BorderColor #E67E22
  ArrowColor #2C3E50
}

object "customer1 : Customer" as C {
  customerId = "CUST-1042"
  name = "Rahul Sharma"
  email = "rahul@gmail.com"
  phone = "+91-9876543210"
  address = "B-12, Koregaon Park, Pune"
}

object "restaurant1 : Restaurant" as R {
  restaurantId = "REST-201"
  name = "Spice Garden"
  rating = 4.5
  cuisineType = "Indian"
  isOpen = true
}

object "menuItem1 : MenuItem" as MI {
  itemId = "ITEM-101"
  name = "Paneer Butter Masala"
  price = 220.00
  category = "Main Course"
  isAvailable = true
}

object "order1 : Order" as O {
  orderId = "ORD-78945"
  status = "OutForDelivery"
  totalAmount = 450.00
  placedAt = "2026-05-03 12:30"
  deliveredAt = null
}

object "driver1 : DeliveryDriver" as D {
  driverId = "DRV-302"
  name = "Amit Kumar"
  phone = "+91-9988776655"
  rating = 4.7
  currentLocation = "18.5204° N, 73.8567° E"
}

object "payment1 : Payment" as P {
  paymentId = "PAY-56321"
  method = "UPI"
  amount = 450.00
  status = "Captured"
  transactionId = "TXN-ABC123"
}

C --> O : places
R --> MI : offers
O --> R : from
O --> D : assignedTo
O --> P : has
@enduml""",

    "ecommerce": """@startuml
skinparam object {
  BackgroundColor #D6EAF8
  BorderColor #2980B9
  ArrowColor #2C3E50
}

object "customer1 : Customer" as C {
  customerId = "CUST-5521"
  name = "Priya Patel"
  email = "priya@example.com"
  shippingAddress = "45, MG Road, Bangalore"
}

object "product1 : Product" as PR {
  productId = "PROD-8821"
  name = "Wireless Headphones"
  price = 2499.00
  stock = 50
  category = "Electronics"
}

object "order1 : Order" as O {
  orderId = "ORD-99231"
  status = "Shipped"
  totalAmount = 2499.00
  orderDate = "2026-05-01"
}

object "cart1 : Cart" as CA {
  cartId = "CART-1122"
  totalItems = 1
  subtotal = 2499.00
}

object "payment1 : Payment" as P {
  paymentId = "PAY-33441"
  method = "Credit Card"
  amount = 2499.00
  status = "Captured"
}

C --> CA : has
CA --> PR : contains
C --> O : places
O --> P : has
O --> PR : contains
@enduml""",

    "general": """@startuml
skinparam object {
  BackgroundColor #F0F3F4
  BorderColor #717D7E
  ArrowColor #2C3E50
}

object "user1 : User" as U {
  userId = "USR-001"
  username = "john_doe"
  email = "john@example.com"
  role = "admin"
  createdAt = "2026-01-01"
}

object "session1 : Session" as S {
  sessionId = "SESS-ABC123"
  createdAt = "2026-05-03 10:00"
  expiresAt = "2026-05-03 18:00"
  ipAddress = "192.168.1.10"
}

object "notification1 : Notification" as N {
  notificationId = "NOTIF-001"
  message = "Your request has been processed"
  isRead = false
  createdAt = "2026-05-03 10:05"
}

U --> S : creates
U --> N : receives
@enduml""",
}


class ObjectDiagramGenerator:
    """Domain-aware object diagram generator with realistic sample instance data"""

    @classmethod
    def generate(cls, classes: List[str] = None, attributes: Dict[str, List[str]] = None,
                 raw_input: str = "", domain: str = "general") -> Dict[str, Any]:
        """Generate PlantUML object diagram with domain-specific sample instances"""
        combined = raw_input
        detected_domain = cls._detect_domain(combined.lower(), domain)

        plantuml_code = DOMAIN_OBJECT_DIAGRAMS.get(detected_domain, DOMAIN_OBJECT_DIAGRAMS["general"])

        return {
            "plantuml": plantuml_code,
            "domain": detected_domain,
            "classes": classes or [],
        }

    @classmethod
    def _detect_domain(cls, text: str, hint: str) -> str:
        if hint and hint != "general" and hint in DOMAIN_OBJECT_DIAGRAMS:
            return hint
        if any(w in text for w in ["food", "delivery", "restaurant", "meal", "menu"]):
            return "food_delivery"
        if any(w in text for w in ["shop", "ecommerce", "product", "cart"]):
            return "ecommerce"
        return "general"