import asyncio
from backend.app.main import process_input
from backend.app.database.connection import SessionLocal
from backend.app.database.models import User

async def main():
    db = SessionLocal()
    user = db.query(User).first()
    try:
        res = await process_input("Healthcare App", db, user)
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
