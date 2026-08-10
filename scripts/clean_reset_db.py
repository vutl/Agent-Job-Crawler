import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from packages.database import Base, engine, SessionLocal
from scripts.ingest_all_real_data import main as seed_main
from scripts.reanalyze_database import main as reanalyze_main

def main():
    print("Resetting database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database tables recreated cleanly!")

    asyncio.run(seed_main())
    asyncio.run(reanalyze_main())

if __name__ == "__main__":
    main()
