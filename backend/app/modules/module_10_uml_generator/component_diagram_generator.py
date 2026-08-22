"""Generate Component diagrams from requirements and project description (domain-aware N-tier architecture)"""
from typing import List, Dict, Any
import re

DOMAIN_COMPONENTS = {
    "food_delivery": """@startuml
skinparam componentStyle uml2
skinparam component {
  BackgroundColor #D5E8D4
  BorderColor #82B366
}
skinparam interfaceBackgroundColor #DAE8FC
skinparam interfaceBorderColor #6C8EBF
skinparam arrowColor #333333
skinparam packageBackgroundColor #FFF9C4
skinparam packageBorderColor #D6B600

package "Client Layer" {
  [Customer Mobile App] as CMA
  [Restaurant Dashboard] as RD
  [Driver App] as DA
}

package "API Gateway" {
  [Load Balancer] as LB
  [API Gateway\\n(Rate Limiting, Auth)] as APIGW
}

package "Microservices" {
  [User Service] as US
  [Order Service] as OS
  [Restaurant Service] as RS
  [Payment Service] as PS
  [Delivery Tracking Service] as DTS
  [Notification Service] as NS
  [Search Service] as SS
}

package "Data Layer" {
  database "Users DB\\n(PostgreSQL)" as UDB
  database "Orders DB\\n(PostgreSQL)" as ODB
  database "Restaurants DB\\n(PostgreSQL)" as RDB
  database "Cache\\n(Redis)" as CACHE
}

package "External Services" {
  [Payment Gateway\\n(Stripe/Razorpay)] as PG
  [Maps API\\n(Google Maps)] as MAPS
  [SMS/Push\\n(Firebase/Twilio)] as PUSH
}

CMA --> LB
RD --> LB
DA --> LB
LB --> APIGW
APIGW --> US
APIGW --> OS
APIGW --> RS
APIGW --> PS
APIGW --> DTS
APIGW --> NS
APIGW --> SS

US --> UDB
OS --> ODB
RS --> RDB
OS --> CACHE
SS --> CACHE

PS --> PG
DTS --> MAPS
NS --> PUSH
@enduml""",

    "ecommerce": """@startuml
skinparam componentStyle uml2
skinparam component {
  BackgroundColor #DAE8FC
  BorderColor #6C8EBF
}
skinparam packageBackgroundColor #FFF2CC
skinparam packageBorderColor #D6B600

package "Frontend" {
  [Web Application\\n(React/Next.js)] as WEB
  [Mobile App\\n(iOS/Android)] as MOBILE
}

package "Backend Services" {
  [API Gateway] as APIGW
  [Product Service] as PRODS
  [Order Service] as ORDS
  [User Service] as USRS
  [Payment Service] as PAYS
  [Inventory Service] as INVS
  [Search Service\\n(Elasticsearch)] as SEARCH
  [Recommendation Engine] as REC
}

package "Data Layer" {
  database "Products DB" as PDB
  database "Orders DB" as ODB
  database "Users DB" as UDB
  database "Cache (Redis)" as CACHE
}

package "External" {
  [Payment Gateway] as PG
  [Email Service] as EMAIL
  [Shipping API] as SHIP
}

WEB --> APIGW
MOBILE --> APIGW
APIGW --> PRODS
APIGW --> ORDS
APIGW --> USRS
APIGW --> PAYS
APIGW --> SEARCH
APIGW --> REC
PRODS --> PDB
ORDS --> ODB
USRS --> UDB
PAYS --> PG
ORDS --> EMAIL
ORDS --> SHIP
SEARCH --> CACHE
@enduml""",

    "general": """@startuml
skinparam componentStyle uml2
skinparam component {
  BackgroundColor #E8DAEF
  BorderColor #7D3C98
}
skinparam packageBackgroundColor #F0F3F4
skinparam packageBorderColor #717D7E

package "Presentation Layer" {
  [Web UI] as WEB
  [Mobile App] as MOBILE
}

package "Application Layer" {
  [API Gateway] as APIGW
  [Business Logic Service] as BLS
  [Authentication Service] as AUTH
  [Notification Service] as NS
}

package "Data Layer" {
  database "Primary Database\\n(PostgreSQL)" as DB
  database "Cache\\n(Redis)" as CACHE
  [File Storage\\n(S3/MinIO)] as FILES
}

package "External Integrations" {
  [Email Service] as EMAIL
  [Payment Gateway] as PG
}

WEB --> APIGW
MOBILE --> APIGW
APIGW --> AUTH
APIGW --> BLS
BLS --> DB
BLS --> CACHE
BLS --> FILES
BLS --> NS
NS --> EMAIL
BLS --> PG
@enduml""",
}


class ComponentDiagramGenerator:
    """Domain-aware component/architecture diagram generator"""

    @staticmethod
    def generate(requirements: List[Dict] = None, raw_input: str = "", domain: str = "general") -> Dict[str, Any]:
        """Generate PlantUML component diagram with N-tier architecture"""
        if requirements is None:
            requirements = []
        combined = raw_input + " " + " ".join(r.get("text", "") for r in requirements)
        detected_domain = ComponentDiagramGenerator._detect_domain(combined.lower(), domain)

        plantuml_code = DOMAIN_COMPONENTS.get(detected_domain, DOMAIN_COMPONENTS["general"])

        return {
            "plantuml": plantuml_code,
            "domain": detected_domain,
        }

    @staticmethod
    def _detect_domain(text: str, hint: str) -> str:
        if hint and hint != "general" and hint in DOMAIN_COMPONENTS:
            return hint
        if any(w in text for w in ["food", "delivery", "restaurant", "meal"]):
            return "food_delivery"
        if any(w in text for w in ["shop", "ecommerce", "product", "cart"]):
            return "ecommerce"
        return "general"