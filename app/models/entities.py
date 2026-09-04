from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    DateTime,
    Boolean,
    Integer,
    Float,
    JSON,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


def uuid_pk():
    return mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()), index=True)


class School(Base):
    __tablename__ = "schools"

    id: Mapped[str] = uuid_pk()
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    school_type: Mapped[str] = mapped_column(String(50), default="Secondary")
    primary_color: Mapped[str] = mapped_column(String(20), default="#14213D")
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    role_id: Mapped[str] = mapped_column(ForeignKey("roles.id"))
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Family(Base):
    __tablename__ = "families"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    household_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    billing_contact_parent_id: Mapped[str | None] = mapped_column(ForeignKey("parents.id"))
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Parent(Base):
    __tablename__ = "parents"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    family_id: Mapped[str] = mapped_column(ForeignKey("families.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    relationship: Mapped[str] = mapped_column(String(50), default="Parent")
    email: Mapped[str] = mapped_column(String(150))
    phone: Mapped[str] = mapped_column(String(30))
    preferred_channel: Mapped[str] = mapped_column(String(30), default="email")
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    family_id: Mapped[str] = mapped_column(ForeignKey("families.id"), index=True)
    class_id: Mapped[str] = mapped_column(ForeignKey("classes.id"), index=True)
    lead_id: Mapped[str | None] = mapped_column(ForeignKey("leads.id"))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    admission_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    gender: Mapped[str] = mapped_column(String(20))
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    arm: Mapped[str] = mapped_column(String(10))
    level_group: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_name: Mapped[str] = mapped_column(String(150), nullable=False)
    parent_phone: Mapped[str] = mapped_column(String(30), nullable=False)
    parent_email: Mapped[str] = mapped_column(String(150))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    stage: Mapped[str] = mapped_column(String(50), default="new", index=True)
    interested_class: Mapped[str] = mapped_column(String(50))
    follow_up_at: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    term: Mapped[str] = mapped_column(String(50), nullable=False)
    amount_due: Mapped[float] = mapped_column(Float, nullable=False)
    amount_paid: Mapped[float] = mapped_column(Float, default=0)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="issued", index=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"), index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_reference: Mapped[str] = mapped_column(String(100))
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    family_id: Mapped[str] = mapped_column(ForeignKey("families.id"), index=True)
    parent_id: Mapped[str] = mapped_column(ForeignKey("parents.id"), index=True)
    assignee_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    priority: Mapped[str] = mapped_column(String(30), default="Medium", index=True)
    status: Mapped[str] = mapped_column(String(30), default="open", index=True)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MessageLog(Base):
    __tablename__ = "message_logs"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    recipient: Mapped[str] = mapped_column(String(150), nullable=False)
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(30), default="queued")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    user_id: Mapped[str | None] = mapped_column(String(40))
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(40))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    meta_data: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BusRoute(Base):
    __tablename__ = "bus_routes"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    route_name: Mapped[str] = mapped_column(String(150), nullable=False)
    route_code: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    driver_name: Mapped[str | None] = mapped_column(String(150))
    vehicle_number: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BusStop(Base):
    __tablename__ = "bus_stops"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    route_id: Mapped[str] = mapped_column(ForeignKey("bus_routes.id"), index=True)
    stop_name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str | None] = mapped_column(Text)
    stop_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class StudentTransport(Base):
    __tablename__ = "student_transport"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"), index=True)
    route_id: Mapped[str] = mapped_column(ForeignKey("bus_routes.id"), index=True)
    stop_id: Mapped[str | None] = mapped_column(ForeignKey("bus_stops.id"))
    pickup_location: Mapped[str | None] = mapped_column(Text)
    dropoff_location: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = uuid_pk()
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"), index=True)
    vehicle_number: Mapped[str] = mapped_column(String(50), nullable=False)
    vehicle_type: Mapped[str] = mapped_column(String(50))
    capacity: Mapped[int] = mapped_column(Integer, default=0)
    driver_name: Mapped[str | None] = mapped_column(String(150))
    driver_phone: Mapped[str | None] = mapped_column(String(30))
    last_known_lat: Mapped[float | None] = mapped_column(Float)
    last_known_lng: Mapped[float | None] = mapped_column(Float)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(30), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
