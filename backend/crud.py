from sqlalchemy.orm import Session
from . import models, schemas
import uuid
import datetime # <--- SE AÑADIÓ ESTA LÍNEA
from typing import List, Optional

# --- Funciones Auxiliares ---
def generate_id():
    """Genera un ID único similar a los de Firebase."""
    return uuid.uuid4().hex[:20] # 20 caracteres como ejemplo

# --- Admin Users CRUD ---
def get_admin_user(db: Session, user_id: str) -> Optional[models.AdminUser]:
    return db.query(models.AdminUser).filter(models.AdminUser.AdminUserID == user_id).first()

def get_admin_user_by_email(db: Session, email: str) -> Optional[models.AdminUser]:
    return db.query(models.AdminUser).filter(models.AdminUser.Email == email).first()

def get_admin_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.AdminUser]:
    return db.query(models.AdminUser).offset(skip).limit(limit).all()

def create_admin_user(db: Session, user: schemas.AdminUserCreate) -> models.AdminUser:
    db_user = models.AdminUser(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Students CRUD ---
def get_student(db: Session, student_id: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.StudentID == student_id).first()

def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()

def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    student_id = student.StudentID or generate_id()
    db_student = models.Student(**student.dict(exclude={"StudentID"}), StudentID=student_id)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: str, student_update: schemas.StudentUpdate) -> Optional[models.Student]:
    db_student = get_student(db, student_id)
    if db_student:
        update_data = student_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_student, key, value)
        db.commit()
        db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: str) -> Optional[models.Student]:
    db_student = get_student(db, student_id)
    if db_student:
        db.delete(db_student)
        db.commit()
    return db_student

# --- Memberships CRUD ---
def get_membership(db: Session, membership_id: str) -> Optional[models.Membership]:
    return db.query(models.Membership).filter(models.Membership.MembershipID == membership_id).first()

def get_memberships_by_student(db: Session, student_id: str, skip: int = 0, limit: int = 100) -> List[models.Membership]:
    return db.query(models.Membership).filter(models.Membership.StudentID == student_id).offset(skip).limit(limit).all()

def get_memberships(db: Session, skip: int = 0, limit: int = 100) -> List[models.Membership]:
    return db.query(models.Membership).offset(skip).limit(limit).all()

def create_membership(db: Session, membership: schemas.MembershipCreate) -> models.Membership:
    membership_id = membership.MembershipID or generate_id()
    db_membership = models.Membership(**membership.dict(exclude={"MembershipID"}), MembershipID=membership_id)
    db.add(db_membership)
    db.commit()
    db.refresh(db_membership)
    return db_membership

def update_membership(db: Session, membership_id: str, membership_update: schemas.MembershipUpdate) -> Optional[models.Membership]:
    db_membership = get_membership(db, membership_id)
    if db_membership:
        update_data = membership_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_membership, key, value)
        db.commit()
        db.refresh(db_membership)
    return db_membership

def delete_membership(db: Session, membership_id: str) -> Optional[models.Membership]:
    db_membership = get_membership(db, membership_id)
    if db_membership:
        db.delete(db_membership)
        db.commit()
    return db_membership

# --- Attendance CRUD ---
def create_attendance(db: Session, attendance: schemas.AttendanceCreate) -> models.Attendance:
    db_attendance = models.Attendance(**attendance.dict())
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance

def get_attendance_by_student_and_date(db: Session, student_id: str, date: datetime.date) -> List[models.Attendance]:
    start_of_day = datetime.datetime.combine(date, datetime.time.min)
    end_of_day = datetime.datetime.combine(date, datetime.time.max)
    return db.query(models.Attendance).filter(
        models.Attendance.StudentID == student_id,
        models.Attendance.Timestamp >= start_of_day,
        models.Attendance.Timestamp <= end_of_day
    ).all()

def get_attendance_today(db: Session, skip: int = 0, limit: int = 100) -> List[models.Attendance]:
    today = datetime.date.today()
    start_of_day = datetime.datetime.combine(today, datetime.time.min)
    end_of_day = datetime.datetime.combine(today, datetime.time.max)
    return db.query(models.Attendance).filter(
        models.Attendance.Timestamp >= start_of_day,
        models.Attendance.Timestamp <= end_of_day
    ).order_by(models.Attendance.Timestamp.desc()).offset(skip).limit(limit).all()

# --- Routines CRUD ---
def get_routine(db: Session, routine_id: str) -> Optional[models.Routine]:
    return db.query(models.Routine).filter(models.Routine.RoutineID == routine_id).first()

def get_routines_by_student(db: Session, student_id: str, skip: int = 0, limit: int = 100) -> List[models.Routine]:
    return db.query(models.Routine).filter(models.Routine.StudentID == student_id).offset(skip).limit(limit).all()

def create_routine(db: Session, routine: schemas.RoutineCreate) -> models.Routine:
    routine_id = routine.RoutineID or generate_id()
    db_routine = models.Routine(**routine.dict(exclude={"RoutineID"}), RoutineID=routine_id)
    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)
    return db_routine

def update_routine(db: Session, routine_id: str, routine_update: schemas.RoutineUpdate) -> Optional[models.Routine]:
    db_routine = get_routine(db, routine_id)
    if db_routine:
        update_data = routine_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_routine, key, value)
        db.commit()
        db.refresh(db_routine)
    return db_routine

def delete_routine(db: Session, routine_id: str) -> Optional[models.Routine]:
    db_routine = get_routine(db, routine_id)
    if db_routine:
        db.delete(db_routine)
        db.commit()
    return db_routine
