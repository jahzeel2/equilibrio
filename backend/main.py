from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import students, memberships, attendance, routines, admin_users

# Crea las tablas en la base de datos si no existen
# ¡Cuidado! En producción, podrías querer usar migraciones (Alembic).
print("Creando tablas en la base de datos (si no existen)...")
try:
    models.Base.metadata.create_all(bind=engine)
    print("Tablas creadas o ya existentes.")
except Exception as e:
    print(f"Error al crear tablas: {e}")


app = FastAPI(
    title="Sistema de Gestión de Gimnasio API",
    description="API para gestionar alumnos, membresías, asistencia y rutinas.",
    version="1.0.0"
)

# Configuración de CORS (Cross-Origin Resource Sharing)
# Permite que tu frontend (ej. localhost:8001) se comunique con tu backend (ej. localhost:8000)
origins = [
    "http://localhost",
    "http://localhost:8000", # Si tu frontend corre aquí (o el puerto que uses)
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    # Añade aquí la URL de tu frontend si es diferente
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Permite estos orígenes
    allow_credentials=True,
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permite todas las cabeceras
)

# Incluye los routers de cada entidad
app.include_router(admin_users.router)
app.include_router(students.router)
app.include_router(memberships.router)
app.include_router(attendance.router)
app.include_router(routines.router)


@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {"message": "¡Bienvenido a la API del Sistema de Gestión de Gimnasio!"}

# Aquí podrías añadir más lógica, como la autenticación global.