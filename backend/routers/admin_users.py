# routers/admin_users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import crud, models, schemas # '..' para referenciar módulos en el directorio padre
from ..database import get_db

router = APIRouter(
    prefix="/admin_users",
    tags=["Admin Users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.AdminUser, summary="Crear un nuevo usuario administrador")
def create_admin_user(user: schemas.AdminUserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario administrador en la base de datos.
    - **AdminUserID**: Debe ser único (ej. UID de un sistema de autenticación externo).
    - **Email**: Debe ser único.
    """
    db_user_by_id = crud.get_admin_user(db, user_id=user.AdminUserID)
    if db_user_by_id:
        raise HTTPException(status_code=400, detail=f"Admin User ID '{user.AdminUserID}' already registered")
    db_user_by_email = crud.get_admin_user_by_email(db, email=user.Email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail=f"Email '{user.Email}' already registered")
    return crud.create_admin_user(db=db, user=user)

@router.get("/", response_model=List[schemas.AdminUser], summary="Obtener lista de usuarios administradores")
def read_admin_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene una lista paginada de todos los usuarios administradores.
    """
    users = crud.get_admin_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.AdminUser, summary="Obtener un usuario administrador por ID")
def read_admin_user(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene los detalles de un usuario administrador específico por su AdminUserID.
    """
    db_user = crud.get_admin_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Admin User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.AdminUser, summary="Actualizar un usuario administrador")
def update_admin_user(user_id: str, user_update: schemas.AdminUserUpdate, db: Session = Depends(get_db)):
    """
    Actualiza la información de un usuario administrador existente.
    Solo los campos proporcionados en el cuerpo de la solicitud serán actualizados.
    """
    db_user = crud.get_admin_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Admin User not found")

    # Verificar si el nuevo email ya está en uso por otro usuario
    if user_update.Email and user_update.Email != db_user.Email:
        existing_user_with_email = crud.get_admin_user_by_email(db, email=user_update.Email)
        if existing_user_with_email and existing_user_with_email.AdminUserID != user_id:
            raise HTTPException(status_code=400, detail=f"Email '{user_update.Email}' is already in use by another user.")

    # Aplicar la actualización (SQLAlchemy maneja el objeto db_user directamente)
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# Nota: La eliminación de AdminUsers podría tener implicaciones en cascada o SET NULL
# en otras tablas. Considera la lógica de negocio para esto.
# Por simplicidad, no se incluye un endpoint DELETE para AdminUsers aquí,
# ya que podría ser una operación sensible. Si es necesario, se puede añadir.

# Ejemplo de cómo podría ser un endpoint de eliminación (usar con precaución):
# @router.delete("/{user_id}", response_model=schemas.AdminUser, summary="Eliminar un usuario administrador")
# def delete_admin_user(user_id: str, db: Session = Depends(get_db)):
#     db_user = crud.get_admin_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="Admin User not found")
#     
#     # Antes de eliminar, considera qué sucede con los registros que referencian a este admin.
#     # Las FK están configuradas como ON DELETE SET NULL en Students, Memberships, Routines, Attendance.
#     # Para ReminderSettings, es ON DELETE CASCADE.
#
#     db.delete(db_user)
#     db.commit()
#     return db_user
