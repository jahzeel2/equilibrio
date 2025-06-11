# routers/memberships.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas
from ..database import get_db
import uuid # Para generar IDs si no se proporcionan

router = APIRouter(
    prefix="/memberships",
    tags=["Memberships"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.Membership, summary="Crear una nueva membresía")
def create_membership(membership: schemas.MembershipCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva membresía para un alumno.
    - **StudentID**: Debe existir en la tabla de Alumnos.
    - **MembershipID**: Opcional, se generará uno si no se provee.
    """
    db_student = crud.get_student(db, student_id=membership.StudentID)
    if not db_student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{membership.StudentID}' not found. Cannot create membership.")
    
    # Asignar nombre del estudiante si no se proveyó y el estudiante existe
    if not membership.StudentName and db_student:
        membership.StudentName = f"{db_student.Nombre} {db_student.Apellido}".strip()

    # Generar QrCodeData si no se proporcionó
    if not membership.QrCodeData:
        membership.QrCodeData = f"studentId:{membership.StudentID};membershipType:{membership.Type}"

    return crud.create_membership(db=db, membership=membership)

@router.get("/", response_model=List[schemas.Membership], summary="Obtener lista de todas las membresías")
def read_memberships(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene una lista paginada de todas las membresías registradas.
    """
    memberships = crud.get_memberships(db, skip=skip, limit=limit)
    return memberships

@router.get("/student/{student_id}", response_model=List[schemas.Membership], summary="Obtener membresías por ID de alumno")
def read_memberships_by_student(student_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene todas las membresías asociadas a un alumno específico.
    """
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail=f"Student with ID '{student_id}' not found.")
    
    memberships = crud.get_memberships_by_student(db, student_id=student_id, skip=skip, limit=limit)
    return memberships

@router.get("/{membership_id}", response_model=schemas.Membership, summary="Obtener una membresía por ID")
def read_membership(membership_id: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de una membresía específica por su MembershipID.
    """
    db_membership = crud.get_membership(db, membership_id=membership_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    return db_membership

@router.put("/{membership_id}", response_model=schemas.Membership, summary="Actualizar una membresía")
def update_membership(membership_id: str, membership_update: schemas.MembershipUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de una membresía existente.
    Solo los campos proporcionados en el cuerpo de la solicitud serán actualizados.
    Si se cambia StudentID, se actualiza StudentName si es necesario.
    """
    db_membership = crud.get_membership(db, membership_id=membership_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Si se actualiza el StudentID, verificar que el nuevo estudiante exista
    # y actualizar StudentName si no se proporciona explícitamente en el update.
    if membership_update.StudentID and membership_update.StudentID != db_membership.StudentID:
        new_db_student = crud.get_student(db, student_id=membership_update.StudentID)
        if not new_db_student:
            raise HTTPException(status_code=404, detail=f"New Student with ID '{membership_update.StudentID}' not found.")
        # Actualizar StudentName si no se está actualizando explícitamente
        if membership_update.StudentName is None:
            membership_update.StudentName = f"{new_db_student.Nombre} {new_db_student.Apellido}".strip()
    
    # Actualizar QrCodeData si cambia StudentID o Type y no se provee explícitamente
    if (membership_update.StudentID or membership_update.Type) and membership_update.QrCodeData is None:
        current_student_id = membership_update.StudentID or db_membership.StudentID
        current_type = membership_update.Type or db_membership.Type
        membership_update.QrCodeData = f"studentId:{current_student_id};membershipType:{current_type}"


    updated_membership = crud.update_membership(db, membership_id=membership_id, membership_update=membership_update)
    return updated_membership


@router.delete("/{membership_id}", response_model=schemas.Membership, summary="Eliminar una membresía")
def delete_membership(membership_id: str, db: Session = Depends(get_db)):
    """
    Elimina una membresía de la base de datos.
    Advertencia: Esto podría afectar registros de asistencia si están configurados
    con ON DELETE NO ACTION (la eliminación fallará si hay asistencias referenciándola).
    """
    db_membership = crud.get_membership(db, membership_id=membership_id)
    if db_membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    # Verificar si hay registros de asistencia que referencian esta membresía
    # La FK en Attendance a Memberships es ON DELETE NO ACTION
    # por lo que SQL Server debería prevenir la eliminación si hay referencias.
    # No es estrictamente necesario chequearlo aquí en la app si la BD lo maneja,
    # pero podría dar un mensaje de error más amigable.
    
    # Ejemplo de chequeo (opcional):
    # attendance_references = db.query(models.Attendance).filter(models.Attendance.MembershipID == membership_id).first()
    # if attendance_references:
    #     raise HTTPException(status_code=400, detail="Cannot delete membership. It is referenced by attendance records.")

    deleted_membership = crud.delete_membership(db, membership_id=membership_id)
    if deleted_membership is None: # Debería ser redundante si el get_membership anterior funcionó
        raise HTTPException(status_code=404, detail="Membership not found during deletion process")
    return deleted_membership
