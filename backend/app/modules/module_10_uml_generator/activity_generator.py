"""Generate Activity diagrams from requirements and project description (domain-aware workflows)"""
from typing import List, Dict, Any
import re

# Domain-specific activity flows
DOMAIN_ACTIVITIES = {
    "food_delivery": """@startuml
skinparam activityBackgroundColor #E8F8F5
skinparam activityBorderColor #1ABC9C
skinparam arrowColor #2C3E50
skinparam activityFontSize 12

|Customer|
start
:Open food delivery app;
:Browse restaurants by location;
:View restaurant menu;
:Add items to cart;
:Review cart & apply coupon;

|Payment System|
:Enter delivery address;
:Select payment method;
if (Payment valid?) then (Yes)
  :Deduct from wallet / charge card;
else (No)
  :Show payment error;
  :Retry payment;
endif

|Order Service|
:Create order with status: PENDING;
:Notify restaurant;

|Restaurant|
if (Accept order?) then (Yes)
  :Update status: ACCEPTED;
  :Prepare food items;
  :Mark ready for pickup;
else (No)
  :Reject order;
  :Notify customer & refund;
  stop
endif

|Delivery Driver|
:Receive pickup notification;
:Accept delivery task;
:Pick up order from restaurant;
:Update status: OUT_FOR_DELIVERY;
:Navigate to customer address;

|Customer|
:Track driver in real-time;
:Receive delivery notification;

|Delivery Driver|
:Mark order: DELIVERED;

|Customer|
:Confirm receipt;
:Rate the restaurant & driver;
stop
@enduml""",

    "ecommerce": """@startuml
skinparam activityBackgroundColor #EBF5FB
skinparam activityBorderColor #2980B9
skinparam arrowColor #2C3E50
skinparam activityFontSize 12

|Customer|
start
:Visit ecommerce platform;
:Search or browse products;
:View product details & reviews;
:Add to cart;
:Proceed to checkout;
:Enter shipping address;

|Payment Service|
:Enter payment details;
if (Payment successful?) then (Yes)
  :Payment confirmed;
else (No)
  :Show error message;
  :Retry or choose different method;
  stop
endif

|Order Service|
:Create order record;
:Send confirmation email;

|Inventory Service|
:Reserve inventory;
:Update stock count;

|Seller|
:Receive order notification;
:Pack items;
:Hand over to shipping;

|Shipping Service|
:Generate tracking number;
:Dispatch package;

|Customer|
:Track shipment;
:Receive delivery;
:Confirm delivery;
if (Satisfied?) then (Yes)
  :Write product review;
  stop
else (No)
  :Initiate return/refund;
  stop
endif
@enduml""",

    "general": """@startuml
skinparam activityBackgroundColor #F4F6F7
skinparam activityBorderColor #566573
skinparam arrowColor #2C3E50
skinparam activityFontSize 12

|User|
start
:Access the application;
if (Already registered?) then (Yes)
  :Login with credentials;
  if (Credentials valid?) then (Yes)
    :Access granted;
  else (No)
    :Show error;
    :Retry or reset password;
  endif
else (No)
  :Register new account;
  :Verify email;
  :Complete profile;
endif

:Navigate to desired feature;
:Perform core action;

|System|
:Validate input;
if (Valid?) then (Yes)
  :Process request;
  :Update database;
  :Return success response;
else (No)
  :Return validation errors;
endif

|User|
:View result;
:Logout or continue;
stop
@enduml""",
}


class ActivityGenerator:
    """Domain-aware activity diagram generator with swimlane support"""

    @classmethod
    def generate(cls, requirements: List[Dict], raw_input: str = "", domain: str = "general") -> Dict[str, Any]:
        """Generate PlantUML activity diagram with swimlanes"""
        combined = raw_input + " " + " ".join(r.get("text", "") for r in requirements)
        detected_domain = cls._detect_domain(combined.lower(), domain)

        plantuml_code = DOMAIN_ACTIVITIES.get(detected_domain, DOMAIN_ACTIVITIES["general"])

        return {
            "plantuml": plantuml_code,
            "domain": detected_domain,
            "workflow": "domain_specific_activity_flow",
        }

    @classmethod
    def _detect_domain(cls, text: str, hint: str) -> str:
        if hint and hint != "general" and hint in DOMAIN_ACTIVITIES:
            return hint
        if any(w in text for w in ["food", "delivery", "restaurant", "meal", "menu"]):
            return "food_delivery"
        if any(w in text for w in ["shop", "cart", "ecommerce", "product", "sell"]):
            return "ecommerce"
        return "general"
