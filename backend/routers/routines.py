# routers/routines.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas
from ..database import get_db
import uuid # Para generar IDs si no se proporcionan

router = APIRouter(
    prefix="/routines",
    tags=["Routines"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Routine, summary="Crear o asignar una nueva rutina")
def create_routine(routine: schemas.RoutineCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva rutina y la asigna a un alumno.
    - **StudentID**: Debe existir.
    - **RoutineID**: Opcional, se generará uno si no se provee.
    """
    db_student = crud.get_student(db, student_id=routine.StudentID)
    if not db_student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{routine.StudentID}' not found. Cannot create routine.")

    if not routine.StudentName: # Auto-llenar nombre del estudiante
        routine.StudentName = f"{db_student.Nombre} {db_student.Apellido}".strip()
        
    return crud.create_routine(db=db, routine=routine)

@router.get("/student/{student_id}", response_model=List[schemas.Routine], summary="Obtener rutinas por ID de alumno")
def read_routines_by_student(student_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene todas las rutinas asignadas a un alumno específico.
    """
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
        
    routines = crud.get_routines_by_student(db, student_id=student_id, skip=skip, limit=limit)
    return routines

@router.get("/{routine_id}", response_model=schemas.Routine, summary="Obtener una rutina por ID")
def read_routine(routine_id: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de una rutina específica por su RoutineID.
    """
    db_routine = crud.get_routine(db, routine_id=routine_id)
    if db_routine is None:
        raise HTTPException(status_code=404, detail="Routine not found")
    return db_routine

@router.put("/{routine_id}", response_model=schemas.Routine, summary="Actualizar una rutina")
def update_routine(routine_id: str, routine_update: schemas.RoutineUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de una rutina existente.
    Solo los campos proporcionados en el cuerpo de la solicitud serán actualizados.
    """
    db_routine = crud.get_routine(db, routine_id=routine_id)
    if db_routine is None:
        raise HTTPException(status_code=404, detail="Routine not found")

    # Si se actualiza el StudentID, verificar que el nuevo estudiante exista
    # y actualizar StudentName si no se proporciona explícitamente en el update.
    if routine_update.StudentID and routine_update.StudentID != db_routine.StudentID:
        new_db_student = crud.get_student(db, student_id=routine_update.StudentID)
        if not new_db_student:
            raise HTTPException(status_code=404, detail=f"New Student with ID '{routine_update.StudentID}' not found.")
        if routine_update.StudentName is None: # Actualizar solo si no se está cambiando explícitamente
            routine_update.StudentName = f"{new_db_student.Nombre} {new_db_student.Apellido}".strip()

    updated_routine = crud.update_routine(db, routine_id=routine_id, routine_update=routine_update)
    return updated_routine

@router.delete("/{routine_id}", response_model=schemas.Routine, summary="Eliminar una rutina")
def delete_routine(routine_id: str, db: Session = Depends(get_db)):
    """
    Elimina una rutina de la base de datos.
    """
    db_routine = crud.delete_routine(db, routine_id=routine_id)
    if db_routine is None:
        raise HTTPException(status_code=404, detail="Routine not found")
    return db_routine
