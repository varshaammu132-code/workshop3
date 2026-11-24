"""
CRUD (Create, Read, Update, Delete) database operations for Students.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from .models import Student
from .schemas import StudentCreate, StudentUpdate


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """Fetch a single student by primary key ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_usn(db: Session, usn: str) -> Optional[Student]:
    """Fetch a single student by unique USN."""
    return db.query(Student).filter(Student.usn == usn.strip().upper()).first()


def get_students(
    db: Session,
    search: Optional[str] = None,
    department: Optional[str] = None,
    semester: Optional[int] = None,
    skip: int = 0,
    limit: int = 200
) -> List[Student]:
    """
    Fetch a list of students with optional search query, department, or semester filters.
    Orders results with newest students first.
    """
    query = db.query(Student)

    # Search filter across Name or USN
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Student.name.ilike(term),
                Student.usn.ilike(term)
            )
        )

    # Department filter
    if department and department.strip() and department.lower() != "all":
        query = query.filter(Student.department == department.strip())

    # Semester filter
    if semester and semester > 0:
        query = query.filter(Student.semester == semester)

    return query.order_by(Student.id.desc()).offset(skip).limit(limit).all()


def create_student(db: Session, student: StudentCreate) -> Student:
    """Insert a new student into the database."""
    db_student = Student(
        usn=student.usn,
        name=student.name,
        email=str(student.email),
        phone=student.phone,
        department=student.department,
        semester=student.semester,
        gender=student.gender
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
    """Update fields of an existing student."""
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return None

    # Update only provided attributes
    update_dict = student_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if key == "email" and value is not None:
            value = str(value)
        setattr(db_student, key, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    """Delete a student record by ID. Returns True if deleted, False if not found."""
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        return False

    db.delete(db_student)
    db.commit()
    return True


def get_dashboard_stats(db: Session) -> dict:
    """Compute aggregate counts for the dashboard stats cards."""
    total = db.query(func.count(Student.id)).scalar() or 0

    # Department distribution
    dept_rows = db.query(Student.department, func.count(Student.id)).group_by(Student.department).all()
    dept_dist = {dept: count for dept, count in dept_rows}

    # Semester distribution
    sem_rows = db.query(Student.semester, func.count(Student.id)).group_by(Student.semester).all()
    sem_dist = {f"Sem {sem}": count for sem, count in sorted(sem_rows, key=lambda x: x[0])}

    # Gender distribution
    gender_rows = db.query(Student.gender, func.count(Student.id)).group_by(Student.gender).all()
    gender_dist = {gender: count for gender, count in gender_rows}

    return {
        "total_students": total,
        "departments_count": len(dept_dist),
        "department_distribution": dept_dist,
        "semester_distribution": sem_dist,
        "gender_distribution": gender_dist
    }


def seed_sample_students(db: Session):
    """Seed sample data if the student table is currently empty."""
    if db.query(Student).count() > 0:
        return  # Data already exists

    sample_students = [
        Student(
            usn="1MS21CS001",
            name="Aarav Sharma",
            email="aarav.sharma@example.edu",
            phone="9876543210",
            department="Computer Science",
            semester=6,
            gender="Male"
        ),
        Student(
            usn="1MS21IS014",
            name="Ananya Verma",
            email="ananya.v@example.edu",
            phone="9811223344",
            department="Information Science",
            semester=6,
            gender="Female"
        ),
        Student(
            usn="1MS22EC032",
            name="Rohan Nair",
            email="rohan.nair@example.edu",
            phone="9123456780",
            department="Electronics & Comm.",
            semester=4,
            gender="Male"
        ),
        Student(
            usn="1MS22AI009",
            name="Priya Patel",
            email="priya.p@example.edu",
            phone="9988776655",
            department="AI & Machine Learning",
            semester=4,
            gender="Female"
        ),
        Student(
            usn="1MS23ME045",
            name="Vikram Singh",
            email="vikram.s@example.edu",
            phone="9765432109",
            department="Mechanical Engineering",
            semester=2,
            gender="Male"
        ),
        Student(
            usn="1MS23CV018",
            name="Sneha Kulkarni",
            email="sneha.k@example.edu",
            phone="9845012345",
            department="Civil Engineering",
            semester=2,
            gender="Female"
        ),
    ]

    for student in sample_students:
        db.add(student)
    db.commit()
