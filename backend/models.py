from sqlalchemy import Column, String, DateTime, Date, DECIMAL, Boolean, INT, ForeignKey, Computed
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class AdminUser(Base):
    __tablename__ = "AdminUsers"

    AdminUserID = Column(String(255), primary_key=True, index=True)
    Nombre = Column(String(100), nullable=False)
    Apellido = Column(String(100), nullable=True)
    Email = Column(String(255), nullable=False, unique=True, index=True)
    Telefono = Column(String(50), nullable=True)
    Role = Column(String(50), nullable=False, default='admin')
    CreatedAt = Column(DateTime, default=datetime.datetime.utcnow)
    UpdatedAt = Column(DateTime, onupdate=datetime.datetime.utcnow)

    # Relaciones (si aplican, ej: quién creó a los alumnos)
    students_created = relationship("Student", back_populates="creator")
    memberships_created = relationship("Membership", back_populates="creator")
    routines_created = relationship("Routine", back_populates="creator")
    attendance_processed = relationship("Attendance", back_populates="processor")
    reminder_settings = relationship("ReminderSetting", back_populates="admin", uselist=False)

class Student(Base):
    __tablename__ = "Students"

    StudentID = Column(String(255), primary_key=True, index=True)
    Nombre = Column(String(100), nullable=False)
    Apellido = Column(String(100), nullable=False)
    Email = Column(String(255), nullable=True, unique=True, index=True)
    Telefono = Column(String(50), nullable=True)
    FechaNacimiento = Column(Date, nullable=True)
    Direccion = Column(String(500), nullable=True)
    SearchableName = Column(String(201), Computed("LOWER(ISNULL(Nombre, '') + ' ' + ISNULL(Apellido, ''))", persisted=True))
    CreatedAt = Column(DateTime, default=datetime.datetime.utcnow)
    UpdatedAt = Column(DateTime, onupdate=datetime.datetime.utcnow)
    AdminUserID = Column(String(255), ForeignKey("AdminUsers.AdminUserID"))

    creator = relationship("AdminUser", back_populates="students_created")
    memberships = relationship("Membership", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    routines = relationship("Routine", back_populates="student", cascade="all, delete-orphan")

class Membership(Base):
    __tablename__ = "Memberships"

    MembershipID = Column(String(255), primary_key=True, index=True)
    StudentID = Column(String(255), ForeignKey("Students.StudentID"), nullable=False)
    StudentName = Column(String(200), nullable=True)
    Type = Column(String(100), nullable=False)
    StartDate = Column(DateTime, nullable=False)
    EndDate = Column(DateTime, nullable=False)
    Amount = Column(DECIMAL(10, 2), nullable=False)
    PaymentStatus = Column(String(50), nullable=False, default='pendiente')
    QrCodeData = Column(String, nullable=True)
    CreatedAt = Column(DateTime, default=datetime.datetime.utcnow)
    UpdatedAt = Column(DateTime, onupdate=datetime.datetime.utcnow)
    LastPaymentDate = Column(DateTime, nullable=True)
    AdminUserID = Column(String(255), ForeignKey("AdminUsers.AdminUserID"))

    student = relationship("Student", back_populates="memberships")
    creator = relationship("AdminUser", back_populates="memberships_created")
    attendance_link = relationship("Attendance", back_populates="membership_link")

class Attendance(Base):
    __tablename__ = "Attendance"

    AttendanceID = Column(INT, primary_key=True, index=True, autoincrement=True)
    StudentID = Column(String(255), ForeignKey("Students.StudentID"), nullable=False)
    StudentName = Column(String(200), nullable=True)
    Timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    MembershipID = Column(String(255), ForeignKey("Memberships.MembershipID"), nullable=True)
    MembershipType = Column(String(100), nullable=True)
    Status = Column(String(50), nullable=False, default='registrado')
    AdminUserID = Column(String(255), ForeignKey("AdminUsers.AdminUserID"))

    student = relationship("Student", back_populates="attendance_records")
    membership_link = relationship("Membership", back_populates="attendance_link")
    processor = relationship("AdminUser", back_populates="attendance_processed")

class Routine(Base):
    __tablename__ = "Routines"

    RoutineID = Column(String(255), primary_key=True, index=True)
    StudentID = Column(String(255), ForeignKey("Students.StudentID"), nullable=False)
    StudentName = Column(String(200), nullable=True)
    RoutineName = Column(String(255), nullable=False)
    ContentHTML = Column(String, nullable=False) # Usa String sin longitud para NVARCHAR(MAX)
    AssignmentDate = Column(DateTime, default=datetime.datetime.utcnow)
    LastUpdateDate = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    AdminUserID = Column(String(255), ForeignKey("AdminUsers.AdminUserID"))

    student = relationship("Student", back_populates="routines")
    creator = relationship("AdminUser", back_populates="routines_created")

class ReminderSetting(Base):
    __tablename__ = "ReminderSettings"

    ReminderSettingID = Column(INT, primary_key=True, index=True, autoincrement=True)
    AdminUserID = Column(String(255), ForeignKey("AdminUsers.AdminUserID"), nullable=False, unique=True)
    EnableReminders = Column(Boolean, default=True)
    ReminderDays = Column(INT, default=5)
    NotifyEmail = Column(Boolean, default=True)
    NotifySMS = Column(Boolean, default=False)
    UpdatedAt = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    admin = relationship("AdminUser", back_populates="reminder_settings")