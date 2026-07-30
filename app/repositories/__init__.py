from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.school import SchoolRepository
from app.repositories.role import RoleRepository
from app.repositories.class_repo import ClassRepository
from app.repositories.lead import LeadRepository
from app.repositories.family import FamilyRepository
from app.repositories.student import StudentRepository
from app.repositories.parent import ParentRepository
from app.repositories.invoice import InvoiceRepository
from app.repositories.payment import PaymentRepository
from app.repositories.ticket import TicketRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "SchoolRepository",
    "RoleRepository",
    "ClassRepository",
    "LeadRepository",
    "FamilyRepository",
    "StudentRepository",
    "ParentRepository",
    "InvoiceRepository",
    "PaymentRepository",
    "TicketRepository",
]
