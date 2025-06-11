from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import datetime
from decimal import Decimal

# --- Base Schemas ---
class StudentBase(BaseModel):
    Nombre: str
    Apellido: str
    Email: Optional[EmailStr] = None
    Telefono: Optional[str] = None
    FechaNacimiento: Optional[datetime.date] = None
    Direccion: Optional[str] = None
    AdminUserID: Optional[str] = None

class MembershipBase(BaseModel):
    StudentID: str
    Type: str
    StartDate: datetime.datetime
    EndDate: datetime.datetime
    Amount: Decimal
    PaymentStatus: str = Field(..., pattern=r"^(pagado|pendiente)$") # Valida el status
    StudentName: Optional[str] = None
    QrCodeData: Optional[str] = None
    AdminUserID: Optional[str] = None
    LastPaymentDate: Optional[datetime.datetime] = None

class AttendanceBase(BaseModel):
    StudentID: str
    MembershipID: Optional[str] = None
    Status: str = 'registrado'
    AdminUserID: Optional[str] = None
    StudentName: Optional[str] = None
    MembershipType: Optional[str] = None

class RoutineBase(BaseModel):
    StudentID: str
    RoutineName: str
    ContentHTML: str
    AdminUserID: Optional[str] = None
    StudentName: Optional[str] = None

class AdminUserBase(BaseModel):
    Nombre: str
    Apellido: Optional[str] = None
    Email: EmailStr
    Telefono: Optional[str] = None
    Role: str = 'admin'

# --- Create Schemas ---
class StudentCreate(StudentBase):
    StudentID: Optional[str] = None # Permitir que se genere o se proporcione

class MembershipCreate(MembershipBase):
    MembershipID: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class RoutineCreate(RoutineBase):
    RoutineID: Optional[str] = None

class AdminUserCreate(AdminUserBase):
    AdminUserID: str # El ID debe venir de la autenticación (ej. Firebase UID o similar)

# --- Update Schemas ---
class StudentUpdate(StudentBase):
    Nombre: Optional[str] = None
    Apellido: Optional[str] = None

class MembershipUpdate(MembershipBase):
    StudentID: Optional[str] = None
    Type: Optional[str] = None
    StartDate: Optional[datetime.datetime] = None
    EndDate: Optional[datetime.datetime] = None
    Amount: Optional[Decimal] = None
    PaymentStatus: Optional[str] = None

class RoutineUpdate(RoutineBase):
    StudentID: Optional[str] = None
    RoutineName: Optional[str] = None
    ContentHTML: Optional[str] = None

class AdminUserUpdate(AdminUserBase):
    Nombre: Optional[str] = None
    Email: Optional[EmailStr] = None


# --- Read Schemas (Para respuestas de API) ---
class Student(StudentBase):
    StudentID: str
    CreatedAt: datetime.datetime
    UpdatedAt: Optional[datetime.datetime] = None
    SearchableName: Optional[str] = None

    class Config:
        orm_mode = True

class Membership(MembershipBase):
    MembershipID: str
    CreatedAt: datetime.datetime
    UpdatedAt: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True

class Attendance(AttendanceBase):
    AttendanceID: int
    Timestamp: datetime.datetime

    class Config:
        orm_mode = True

class Routine(RoutineBase):
    RoutineID: str
    AssignmentDate: datetime.datetime
    LastUpdateDate: datetime.datetime

    class Config:
        orm_mode = True

class AdminUser(AdminUserBase):
    AdminUserID: str
    CreatedAt: datetime.datetime
    UpdatedAt: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True