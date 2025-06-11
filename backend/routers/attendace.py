# routers/attendance.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas
from ..database import get_db
import datetime

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Attendance, summary="Registrar nueva asistencia")
def create_attendance_record(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    """
    Registra una nueva entrada de asistencia para un alumno.
    - **StudentID**: Debe existir.
    - **MembershipID**: Opcional, pero recomendado para vincular la asistencia a una membresía específica.
    """
    db_student = crud.get_student(db, student_id=attendance.StudentID)
    if not db_student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{attendance.StudentID}' not found.")

    if not attendance.StudentName: # Auto-llenar nombre del estudiante
        attendance.StudentName = f"{db_student.Nombre} {db_student.Apellido}".strip()

    if attendance.MembershipID:
        db_membership = crud.get_membership(db, membership_id=attendance.MembershipID)
        if not db_membership:
            raise HTTPException(status_code=404, detail=f"Membership with ID '{attendance.MembershipID}' not found.")
        if not attendance.MembershipType: # Auto-llenar tipo de membresía
             attendance.MembershipType = db_membership.Type
    
    return crud.create_attendance(db=db, attendance=attendance)

@router.get("/today", response_model=List[schemas.Attendance], summary="Obtener registros de asistencia de hoy")
def read_attendance_today(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene todos los registros de asistencia del día actual, ordenados por más reciente primero.
    """
    return crud.get_attendance_today(db, skip=skip, limit=limit)

@router.get("/student/{student_id}/date/{date_str}", response_model=List[schemas.Attendance], summary="Obtener asistencia de un alumno en una fecha específica")
def read_attendance_by_student_and_date(student_id: str, date_str: str, db: Session = Depends(get_db)):
    """
    Obtiene los registros de asistencia para un alumno específico en una fecha dada.
    Formato de fecha: YYYY-MM-DD (ej. 2025-06-04)
    """
    try:
        attendance_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")

    return crud.get_attendance_by_student_and_date(db, student_id=student_id, date=attendance_date)

# No se suelen necesitar endpoints PUT o DELETE para registros de asistencia,
# ya que son registros históricos. Si se comete un error, se podría añadir
# una lógica de "anulación" o corrección, pero no una eliminación directa.
# Si necesitas eliminar, puedes añadir un endpoint similar a los otros routers.
