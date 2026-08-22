from backend.app.database.connection import SessionLocal
from backend.app.database.models import User, Project
db = SessionLocal()
user = db.query(User).first()
proj_count = db.query(Project).count() + 1
project = Project(
    project_id=f"PROJ_{proj_count:04d}",
    name="Test",
    raw_input="Test",
    domain="Test",
    user_id=user.id,
    status="processing"
)
db.add(project)
try:
    db.commit()
    print("Success")
except Exception as e:
    print("Error:", str(e))
