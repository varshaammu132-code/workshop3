"""
SQLAlchemy Database Models.
Defines the Student table structure in SQLite.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


class Student(Base):
    """
    Student model representing the 'students' table in SQLite.
    Stores all demographic and academic information for each student.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usn = Column(String(50), unique=True, index=True, nullable=False)       # Unique Student Number
    name = Column(String(100), nullable=False)                              # Full Name
    email = Column(String(120), nullable=False)                             # Email Address
    phone = Column(String(20), nullable=False)                              # Mobile Contact Number
    department = Column(String(100), nullable=False)                        # Branch / Department (e.g. Computer Science)
    semester = Column(Integer, nullable=False)                              # Academic Semester (1 to 8)
    gender = Column(String(20), nullable=False)                             # Male / Female / Other
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Student(id={self.id}, usn='{self.usn}', name='{self.name}', department='{self.department}')>"
