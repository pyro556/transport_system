# db_models.py
"""
SQLAlchemy ORM models for the School Transport Payment System.

Covers Academic Years, Terms, Drivers, Attendants, Buses, Students, and Payments.
Includes all constraints, relationships, and integrity rules.
"""

from datetime import date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean,
    Date, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

# --- Base setup ---
Base = declarative_base()
DEFAULT_DB = "sqlite:///transport_system.db"


def init_engine(db_url: str = DEFAULT_DB):
    """Initialize database engine."""
    return create_engine(db_url, echo=False, future=True)


def create_session(engine):
    """Create and return a new session for DB interaction."""
    Session = sessionmaker(bind=engine, autoflush=False)
    return Session()


# =======================
# === MODEL CLASSES ====
# =======================

class AcademicYear(Base):
    """Defines one academic year (e.g. 2024/2025)."""

    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # One academic year → many terms
    terms = relationship("Term", back_populates="academic_year", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("start_date < end_date", name="check_year_dates"),
    )


class Term(Base):
    """A term within an academic year (e.g. Term 1, Term 2, etc.)."""

    __tablename__ = "terms"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"))

    # Relationship back to AcademicYear
    academic_year = relationship("AcademicYear", back_populates="terms")
    # Each term can have many payments
    payments = relationship("Payment", back_populates="term", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("name", "academic_year_id", name="uq_term_name_per_year"),
        CheckConstraint("start_date < end_date", name="check_term_dates"),
    )


class Driver(Base):
    """Represents a bus driver."""

    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=False)
    license_number = Column(String, unique=True, nullable=True)
    assigned = Column(Boolean, default=False)  # Marked true if currently assigned

    # One driver → many buses (in case of reassignments)
    buses = relationship("Bus", back_populates="driver")


class Attendant(Base):
    """Represents a bus attendant."""

    __tablename__ = "attendants"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)

    # One attendant → one bus
    buses = relationship("Bus", back_populates="attendant")


class Bus(Base):
    """Represents a school bus, linked to a driver and an attendant."""

    __tablename__ = "buses"

    id = Column(Integer, primary_key=True)
    bus_name = Column(String, nullable=False, unique=True)
    plate_number = Column(String, unique=True)
    capacity = Column(Integer)
    driver_id = Column(Integer, ForeignKey("drivers.id", ondelete="SET NULL"))
    attendant_id = Column(Integer, ForeignKey("attendants.id", ondelete="SET NULL"))

    # One bus → many students
    students = relationship("Student", back_populates="bus")
    # One bus → one attendant
    attendant = relationship("Attendant", back_populates="buses")
    # One driver → many buses
    driver = relationship("Driver", back_populates="buses")

    __table_args__ = (
        CheckConstraint("capacity >= 0", name="check_bus_capacity"),
    )


class Student(Base):
    """Represents a student using school transport."""

    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_contact = Column(String)
    address = Column(String)
    bus_id = Column(Integer, ForeignKey("buses.id", ondelete="SET NULL"))
    monthly_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

    # Each student is assigned to one bus
    bus = relationship("Bus", back_populates="students")
    # Each student can make multiple payments
    payments = relationship("Payment", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("monthly_rate >= 0", name="check_student_rate"),
    )


class Payment(Base):
    """Represents a student's transport payment record per term/week."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    term_id = Column(Integer, ForeignKey("terms.id", ondelete="CASCADE"))
    week_number = Column(Integer, nullable=True)
    amount_paid = Column(Float, default=0.0)
    balance_carried = Column(Float, default=0.0)
    payment_date = Column(Date, default=date.today)

    # Payment belongs to one student and one term
    student = relationship("Student", back_populates="payments")
    term = relationship("Term", back_populates="payments")

    __table_args__ = (
        # Prevent duplicate weekly records for same student-term
        UniqueConstraint("student_id", "term_id", "week_number", name="uq_payment_unique"),
        # Data validation constraints
        CheckConstraint("amount_paid >= 0", name="check_payment_amount"),
        CheckConstraint("balance_carried >= 0", name="check_balance_nonnegative"),
        CheckConstraint(
            "week_number IS NULL OR (week_number >= 1 AND week_number <= 20)",
            name="check_week_range"
        ),
    )


class SystemSetting(Base):
    """Stores key-value pairs for global configuration (like default rates, export paths)."""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)


# =======================
# === HELPER METHODS ====
# =======================

def create_all_tables(engine):
    """Create all database tables (if they don't exist)."""
    Base.metadata.create_all(engine)
