"""
Seed script to populate the database with initial demo data.
Run this after running migrations to set up the demo environment.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.core.auth import get_password_hash
from app.models.entities import School, User, Role, Family, Parent, Student, Lead, Class as ClassModel
from app.repositories import SchoolRepository, UserRepository, RoleRepository, FamilyRepository, ParentRepository, StudentRepository, LeadRepository, ClassRepository


def seed_database():
    """Seed the database with initial demo data."""
    print("Starting database seed...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create demo school
        school_repo = SchoolRepository(db)
        existing_school = school_repo.get_by_slug("greenfield-college")
        
        if existing_school:
            print("Demo school already exists. Skipping seed.")
            return
        
        school = school_repo.create(
            name="Greenfield College",
            slug="greenfield-college",
            school_type="Secondary",
            primary_color="#14213D"
        )
        print(f"Created school: {school.name}")
        
        # Create admin role
        role_repo = RoleRepository(db)
        admin_role = role_repo.create(
            school_id=school.id,
            name="school_admin",
            permissions=["all"]
        )
        print(f"Created role: {admin_role.name}")

        # Create parent role
        parent_role = role_repo.create(
            school_id=school.id,
            name="parent",
            permissions=["view_children", "view_invoices", "create_tickets", "view_tickets"]
        )
        print(f"Created role: {parent_role.name}")

        # Create demo user (school admin)
        user_repo = UserRepository(db)
        demo_user = user_repo.create(
            school_id=school.id,
            role_id=admin_role.id,
            full_name="Joy Auta",
            email="admin@greenfieldcollege.ng",
            password_hash=get_password_hash("password123"),
            status="active"
        )
        print(f"Created user: {demo_user.email}")

        # Create demo parent user
        parent_user = user_repo.create(
            school_id=school.id,
            role_id=parent_role.id,
            full_name="Demo Parent",
            email="parent3@edudrive.demo",
            password_hash=get_password_hash("password123"),
            status="active"
        )
        print(f"Created parent user: {parent_user.email}")
        
        # Create classes
        class_repo = ClassRepository(db)
        classes = [
            {"name": "JSS 1", "arm": "A", "level_group": "Junior Secondary"},
            {"name": "JSS 2", "arm": "A", "level_group": "Junior Secondary"},
            {"name": "JSS 3", "arm": "A", "level_group": "Junior Secondary"},
            {"name": "SS 1", "arm": "A", "level_group": "Senior Secondary"},
            {"name": "SS 2", "arm": "A", "level_group": "Senior Secondary"},
            {"name": "SS 3", "arm": "A", "level_group": "Senior Secondary"},
        ]
        
        created_classes = []
        for cls_data in classes:
            cls_obj = class_repo.create(school_id=school.id, **cls_data)
            created_classes.append(cls_obj)
            print(f"Created class: {cls_obj.name}")
        
        # Create demo families
        family_repo = FamilyRepository(db)
        parent_repo = ParentRepository(db)
        student_repo = StudentRepository(db)
        
        families_data = [
            {
                "household_name": "Adebayo Family",
                "guardians": ["Tunde Adebayo", "Funke Adebayo"],
                "students": [
                    {"first_name": "Chidi", "last_name": "Adebayo", "class_name": "SS 2"},
                ]
            },
            {
                "household_name": "Okonkwo Family",
                "guardians": ["Emeka Okonkwo", "Ngozi Okonkwo"],
                "students": [
                    {"first_name": "Obi", "last_name": "Okonkwo", "class_name": "JSS 3"},
                    {"first_name": "Ada", "last_name": "Okonkwo", "class_name": "SS 1"},
                ]
            },
            {
                "household_name": "Ibrahim Family",
                "guardians": ["Ahmed Ibrahim", "Aisha Ibrahim"],
                "students": [
                    {"first_name": "Mus", "last_name": "Ibrahim", "class_name": "JSS 1"},
                ]
            },
        ]
        
        student_counter = 1
        
        for family_data in families_data:
            family = family_repo.create(
                school_id=school.id,
                household_name=family_data["household_name"],
                notes="Demo family"
            )
            
            # Create guardians
            for i, guardian_name in enumerate(family_data["guardians"]):
                parent = parent_repo.create(
                    school_id=school.id,
                    family_id=family.id,
                    full_name=guardian_name,
                    email=f"{guardian_name.lower().replace(' ', '.')}@example.com",
                    phone=f"+234{8000000000 + i}",
                    relationship="Father" if i == 0 else "Mother",
                    preferred_channel="email"
                )
                if i == 0:
                    family_repo.update(family, billing_contact_parent_id=parent.id)
            
            # Create students
            for student_data in family_data["students"]:
                # Find matching class
                target_class = next((c for c in created_classes if c.name == student_data["class_name"]), None)
                class_id = target_class.id if target_class else None
                
                student = student_repo.create(
                    school_id=school.id,
                    family_id=family.id,
                    class_id=class_id,
                    first_name=student_data["first_name"],
                    last_name=student_data["last_name"],
                    admission_no=f"GC{datetime.now().year}{str(student_counter).zfill(3)}",
                    gender="Male",
                    status="active"
                )
                student_counter += 1
            
            print(f"Created family: {family.household_name} with {len(family_data['students'])} students")
        
        # Create demo leads
        lead_repo = LeadRepository(db)
        leads_data = [
            {
                "first_name": "David",
                "last_name": "Okafor",
                "parent_name": "Chinedu Okafor",
                "parent_phone": "+2348012345678",
                "parent_email": "chinedu.okafor@example.com",
                "source": "website",
                "stage": "new",
                "interested_class": "JSS 1"
            },
            {
                "first_name": "Grace",
                "last_name": "Eze",
                "parent_name": "Paul Eze",
                "parent_phone": "+2348023456789",
                "parent_email": "paul.eze@example.com",
                "source": "referral",
                "stage": "contacted",
                "interested_class": "SS 1"
            },
            {
                "first_name": "Samuel",
                "last_name": "Bello",
                "parent_name": "Rahman Bello",
                "parent_phone": "+2348034567890",
                "parent_email": "rahman.bello@example.com",
                "source": "walk_in",
                "stage": "tour_scheduled",
                "interested_class": "JSS 2"
            },
        ]
        
        for lead_data in leads_data:
            lead = lead_repo.create(school_id=school.id, **lead_data)
            print(f"Created lead: {lead.first_name} {lead.last_name}")
        
        print("\n✅ Database seeded successfully!")
        print(f"Demo credentials:")
        print(f"  School Admin:")
        print(f"    Email: admin@greenfieldcollege.ng")
        print(f"    Password: password123")
        print(f"  Parent:")
        print(f"    Email: parent3@edudrive.demo")
        print(f"    Password: password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
