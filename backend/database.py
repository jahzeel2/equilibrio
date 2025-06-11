import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Obtiene la cadena de conexión del .env o usa una por defecto (¡ajusta!)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mssql+pyodbc://sa:YourStrong(!)Password@localhost/GymSystemDB?driver=ODBC+Driver+17+for+SQL+Server")

# Crea el motor de SQLAlchemy
# `pool_pre_ping=True` ayuda a manejar conexiones inactivas.
# `echo=True` es útil para depurar, muestra las consultas SQL. Quítalo en producción.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
    # echo=True
)

# Crea una sesión de base de datos local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos ORM
Base = declarative_base()

# Dependencia para obtener la sesión de BD en cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print(f"Conectando a la base de datos: {SQLALCHEMY_DATABASE_URL}")