# ==============================================================================
# Face Recognition Attendance System - Database Setup & Session Factory
# ==============================================================================

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.models import Base, Department, Course, User

# Session factory placeholder
_SessionFactory = None
_engine = None

logger = logging.getLogger("app.database")

def initialize_database(database_url: str) -> None:
    """
    Creates SQL engines, generates tables, and seeds initial data if missing.
    """
    global _SessionFactory, _engine
    
    # Check SQLite directory structure
    if database_url.startswith("sqlite:///"):
        db_path = database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(db_dir, exist_ok=True)
        
    logger.info(f"Connecting database engine: {database_url}")
    
    # Enforce foreign key constraints on SQLite
    connect_args = {}
    if "sqlite" in database_url:
        connect_args = {"check_same_thread": False}
        
    _engine = create_engine(database_url, connect_args=connect_args)
    
    # Enable SQLite foreign keys at database level
    if "sqlite" in database_url:
        from sqlalchemy import event
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _SessionFactory = sessionmaker(bind=_engine, autoflush=False, autocommit=False)
    
    # Generate tables
    Base.metadata.create_all(_engine)
    logger.info("Database tables generated successfully.")
    
    # Seed default data
    seed_default_data()

def get_session():
    """
    Exposes a transactional session context.
    """
    if _SessionFactory is None:
        raise RuntimeError("Database not initialized. Call initialize_database first.")
    return _SessionFactory()

def seed_default_data() -> None:
    """
    Seeds initial departments and courses if database tables are empty.
    """
    session = get_session()
    try:
        if session.query(Department).count() == 0:
            logger.info("Seeding default academic departments...")
            cse = Department(name="Computer Science & Engineering", code="CSE")
            ece = Department(name="Electronics & Communication Engineering", code="ECE")
            me = Department(name="Mechanical Engineering", code="ME")
            session.add_all([cse, ece, me])
            session.commit()
            
            logger.info("Seeding default academic courses...")
            courses = [
                Course(name="Bachelor of Technology in CSE", code="BTECH-CSE", department_id=cse.id),
                Course(name="Master of Technology in CSE", code="MTECH-CSE", department_id=cse.id),
                Course(name="Bachelor of Technology in ECE", code="BTECH-ECE", department_id=ece.id),
                Course(name="Bachelor of Technology in ME", code="BTECH-ME", department_id=me.id)
            ]
            session.add_all(courses)
            session.commit()
            logger.info("Database seeding successfully completed.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding database: {e}")
    finally:
        session.close()
