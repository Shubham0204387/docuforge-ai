from backend.app.database.connection import SessionLocal
from backend.app.modules.module_1_input_processor.format_detector import FormatDetector
from backend.app.modules.module_1_input_processor.input_validator import InputValidator
from backend.app.modules.module_1_input_processor.domain_classifier import DomainClassifier
from backend.app.modules.module_1_input_processor.bulk_processor import BulkProcessor

db = SessionLocal()
text = "Healthcare App"

print("Detecting format...")
format_info = FormatDetector.detect(text)

print("Validating...")
validation = InputValidator.validate(text)

print("Classifying...")
domain = DomainClassifier.classify(text)

print("Extracting...")
reqs = BulkProcessor.extract_requirements(text)

print("Done!", len(reqs))
