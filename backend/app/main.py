"""
FastAPI Main Application.
Provides REST API endpoints for the Student Management System and serves the frontend.
"""

import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Student
from .schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StatsResponse,
    MessageResponse
)
from . import crud

# Determine frontend static files directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")


# Ensure tables are created at startup / module load
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup & shutdown lifespan event handler.
    Ensures tables exist and seeds sample data if empty.
    """
    Base.metadata.create_all(bind=engine)

    # Seed initial sample data for beginner-friendly testing
    db = next(get_db())
    try:
        crud.seed_sample_students(db)
    finally:
        db.close()

    yield



# Initialize FastAPI app
app = FastAPI(
    title="Student Management System API",
    description="A simple, robust REST API for managing student records with SQLite.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# REST API Endpoints
# ==========================================

@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend service status."""
    return {"status": "ok", "message": "Student Management System API is running smoothly!"}


@app.get("/api/stats", response_model=StatsResponse, tags=["Dashboard"])
def get_stats(db: Session = Depends(get_db)):
    """Retrieve statistical summary for dashboard cards and charts."""
    return crud.get_dashboard_stats(db)


@app.get("/api/students", response_model=List[StudentResponse], tags=["Students"])
def list_students(
    search: Optional[str] = Query(None, description="Search by student Name or USN"),
    department: Optional[str] = Query(None, description="Filter by department name"),
    semester: Optional[int] = Query(None, ge=1, le=8, description="Filter by semester (1-8)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all registered students.
    Supports filtering by search query (Name or USN), department, and semester.
    """
    return crud.get_students(db, search=search, department=department, semester=semester)


@app.get("/api/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def get_student(student_id: int, db: Session = Depends(get_db)):
    """Retrieve a single student record by ID."""
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return student


@app.post("/api/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, tags=["Students"])
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Register a new student.
    Validates that the USN is unique before inserting into the database.
    """
    existing_student = crud.get_student_by_usn(db, student.usn)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with USN '{student.usn}' already exists."
        )
    return crud.create_student(db, student)


@app.put("/api/students/{student_id}", response_model=StudentResponse, tags=["Students"])
def update_student(student_id: int, student_data: StudentUpdate, db: Session = Depends(get_db)):
    """
    Update an existing student's details.
    Checks that the student exists and that any changed USN doesn't collide with another student.
    """
    # Verify student exists
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )

    # If USN is being changed, ensure it's not taken by another student
    if student_data.usn and student_data.usn != student.usn:
        conflict = crud.get_student_by_usn(db, student_data.usn)
        if conflict and conflict.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"USN '{student_data.usn}' is already assigned to another student."
            )

    updated = crud.update_student(db, student_id, student_data)
    return updated


@app.delete("/api/students/{student_id}", response_model=MessageResponse, tags=["Students"])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    """Delete a student record by ID."""
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found."
        )
    return MessageResponse(
        message=f"Student record #{student_id} has been successfully deleted.",
        student_id=student_id
    )


# ==========================================
# Serve Frontend Static Files
# ==========================================
if os.path.exists(FRONTEND_DIR):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    js_dir = os.path.join(FRONTEND_DIR, "js")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index():
        """Serve the frontend single-page application at the root URL."""
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend index.html not found."}

