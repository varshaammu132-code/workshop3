"""
Pydantic Schemas for data validation, serialization, and OpenAPI documentation.
"""

from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, Field, field_validator


class StudentBase(BaseModel):
    """Base schema with common student attributes and validation."""
    usn: str = Field(..., min_length=3, max_length=50, description="University Seat Number (USN), must be unique")
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the student")
    email: EmailStr = Field(..., description="Valid student email address")
    phone: str = Field(..., min_length=7, max_length=15, description="Contact phone number (7-15 digits)")
    department: str = Field(..., min_length=2, max_length=100, description="Academic department or branch")
    semester: int = Field(..., ge=1, le=8, description="Current semester (1 to 8)")
    gender: str = Field(..., pattern="^(Male|Female|Other)$", description="Gender: Male, Female, or Other")

    @field_validator("usn")
    @classmethod
    def normalize_usn(cls, v: str) -> str:
        """Strip whitespace and store USN in uppercase for consistency."""
        clean = v.strip().upper()
        if not clean:
            raise ValueError("USN cannot be empty.")
        return clean

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        """Strip leading/trailing whitespace from student name."""
        clean = v.strip()
        if len(clean) < 2:
            raise ValueError("Student name must have at least 2 characters.")
        return clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Ensure phone contains digits (and optional leading +)."""
        clean = v.strip()
        digits = clean.replace("+", "").replace("-", "").replace(" ", "")
        if not digits.isdigit() or len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 valid digits.")
        return clean


class StudentCreate(StudentBase):
    """Schema for adding a new student record."""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating an existing student (all fields optional)."""
    usn: Optional[str] = Field(None, min_length=3, max_length=50)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=15)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    semester: Optional[int] = Field(None, ge=1, le=8)
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")

    @field_validator("usn")
    @classmethod
    def normalize_usn(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip().upper()
            if not clean:
                raise ValueError("USN cannot be empty.")
            return clean
        return v

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            clean = v.strip()
            if len(clean) < 2:
                raise ValueError("Student name must have at least 2 characters.")
            return clean
        return v


class StudentResponse(StudentBase):
    """Schema for returning student data in API responses."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """Schema for dashboard statistical summary."""
    total_students: int
    departments_count: int
    department_distribution: Dict[str, int]
    semester_distribution: Dict[str, int]
    gender_distribution: Dict[str, int]


class MessageResponse(BaseModel):
    """Standard generic API response message."""
    message: str
    student_id: Optional[int] = None
