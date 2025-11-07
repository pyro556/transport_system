"""
menus/students.py
CLI menu for managing Students in the School Transport System.

Functions:
- list_students(): Display all students with details
- add_student(): Register a new student
- update_student(): Edit existing student info
- delete_student(): Remove a student after confirmation
- students_menu(): Main menu for navigation

Handles input validation, safe rollbacks, and relational integrity.
"""

from sqlalchemy.exc import SQLAlchemyError
from utils.helpers import clear_screen, pause, get_valid_input, is_non_negative_number, is_phone_number, confirm_action, search_list
from db_models import Student, Bus


# -----------------------------------------------------------------------------
# MENU ACTIONS
# -----------------------------------------------------------------------------
def list_students(session):
    """Display all students with search functionality."""
    clear_screen()
    all_students = session.query(Student).all()

    if not all_students:
        print("No students found.\n")
        pause()
        return

    # Search functionality
    search_term = get_valid_input("Search by name (or leave blank for all): ")
    if search_term is None:
        print("Operation cancelled.")
        pause()
        return
    students = search_list(all_students, search_term, key_func=lambda s: s.name)

    if not students:
        print("No students match the search term.\n")
        pause()
        return

    print("=== STUDENT LIST ===\n")
    for s in students:
        bus_name = s.bus.bus_name if s.bus else "None"
        status = "Active" if s.is_active else "Inactive"
        print(
            f"ID: {s.id} | Name: {s.name} | Bus: {bus_name} | "
            f"Rate: {s.monthly_rate:.2f} | Status: {status}"
        )
        print(f"Address: {s.address or '-'} | Contact: {s.parent_contact or '-'}\n")

    pause()


def add_student(session):
    """Register a new student with enhanced validation and retry on errors."""
    clear_screen()
    print("=== ADD NEW STUDENT ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    # Get and validate name
    name = get_valid_input("Full Name: ", lambda x: x.strip(), "⚠️ Name cannot be empty.")
    if name is None:
        print("Operation cancelled.")
        pause()
        return

    # Get and validate parent contact (optional phone validation)
    parent_contact = get_valid_input("Parent Contact (optional): ", lambda x: not x or is_phone_number(x), "⚠️ Invalid phone number format.")
    if parent_contact is None:
        print("Operation cancelled.")
        pause()
        return

    # Get and validate address (optional)
    address = get_valid_input("Address (optional): ")
    if address is None:
        print("Operation cancelled.")
        pause()
        return

    # Get and validate monthly rate
    monthly_rate_input = get_valid_input("Monthly Rate: ", is_non_negative_number, "⚠️ Rate must be a non-negative number.")
    if monthly_rate_input is None:
        print("Operation cancelled.")
        pause()
        return
    monthly_rate = float(monthly_rate_input)

    # --- Assign bus ---
    buses = session.query(Bus).all()
    if not buses:
        print("⚠️ No buses available. Add a bus first.")
        pause()
        return

    print("\nAvailable Buses:")
    for b in buses:
        print(f"{b.id}. {b.bus_name} ({b.plate_number})")

    # Get and validate bus ID
    bus_id_input = get_valid_input("Enter Bus ID (or leave blank for none): ", lambda x: not x or (x.isdigit() and int(x) in [b.id for b in buses]), "⚠️ Invalid Bus ID.")
    if bus_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    bus_id = int(bus_id_input) if bus_id_input else None

    # --- Create student ---
    try:
        new_student = Student(
            name=name,
            parent_contact=parent_contact or None,
            address=address or None,
            bus_id=bus_id,
            monthly_rate=monthly_rate,
        )
        session.add(new_student)
        session.commit()
        print("\n✅ Student added successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Error adding student: {e}")

    pause()


def update_student(session):
    """Edit existing student details with enhanced validation."""
    clear_screen()
    print("=== UPDATE STUDENT ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    students = session.query(Student).all()
    if not students:
        print("⚠️ No students available.")
        pause()
        return

    # --- List all students ---
    for s in students:
        print(f"{s.id}. {s.name} (Bus: {s.bus.bus_name if s.bus else 'None'})")

    # Get and validate student ID
    student_id_input = get_valid_input("\nEnter Student ID to update: ", lambda x: x.isdigit() and int(x) in [s.id for s in students], "⚠️ Invalid Student ID.")
    if student_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    student_id = int(student_id_input)

    student = session.get(Student, student_id)
    if not student:
        print("⚠️ Student not found.")
        pause()
        return

    # --- Editable fields ---
    print("\nLeave blank to keep current value. Type 'cancel' to exit.\n")
    new_name = get_valid_input(f"Name [{student.name}]: ", lambda x: x.strip() or student.name, "⚠️ Name cannot be empty.") or student.name
    if new_name is None:
        print("Operation cancelled.")
        pause()
        return
    new_contact = get_valid_input(f"Parent Contact [{student.parent_contact or '-'}]: ", lambda x: not x or is_phone_number(x), "⚠️ Invalid phone number format.") or student.parent_contact
    if new_contact is None:
        print("Operation cancelled.")
        pause()
        return
    new_address = get_valid_input(f"Address [{student.address or '-'}]: ") or student.address
    if new_address is None:
        print("Operation cancelled.")
        pause()
        return
    new_rate_input = get_valid_input(f"Monthly Rate [{student.monthly_rate}]: ", is_non_negative_number, "⚠️ Rate must be a non-negative number.")
    if new_rate_input is None:
        print("Operation cancelled.")
        pause()
        return
    new_rate = float(new_rate_input) if new_rate_input else student.monthly_rate

    # --- Bus reassignment ---
    buses = session.query(Bus).all()
    print("\nAvailable Buses:")
    for b in buses:
        print(f"{b.id}. {b.bus_name}")
    bus_id_input = get_valid_input(f"New Bus ID (current {student.bus_id or 'None'}): ", lambda x: not x or (x.isdigit() and int(x) in [b.id for b in buses]), "⚠️ Invalid Bus ID.")
    if bus_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    new_bus_id = int(bus_id_input) if bus_id_input else student.bus_id

    # --- Update record ---
    try:
        student.name = new_name
        student.parent_contact = new_contact
        student.address = new_address
        student.monthly_rate = new_rate
        student.bus_id = new_bus_id
        session.commit()
        print("\n✅ Student updated successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Error updating student: {e}")

    pause()


def delete_student(session):
    """Remove a student with enhanced confirmation."""
    clear_screen()
    print("=== DELETE STUDENT ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    students = session.query(Student).all()
    if not students:
        print("⚠️ No students to delete.")
        pause()
        return

    for s in students:
        print(f"{s.id}. {s.name}")

    # Get and validate student ID
    student_id_input = get_valid_input("\nEnter Student ID to delete: ", lambda x: x.isdigit() and int(x) in [s.id for s in students], "⚠️ Invalid Student ID.")
    if student_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    student_id = int(student_id_input)

    student = session.get(Student, student_id)
    if not student:
        print("⚠️ Student not found.")
        pause()
        return

    # Use confirm_action for better UX
    if not confirm_action(f"delete '{student.name}'"):
        print("❎ Deletion cancelled.")
        pause()
        return

    try:
        session.delete(student)
        session.commit()
        print("\n✅ Student deleted successfully.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"❌ Error deleting student: {e}")

    pause()


# -----------------------------------------------------------------------------
# MENU NAVIGATION
# -----------------------------------------------------------------------------
def students_menu(session):
    """Display and handle student management menu with enhanced options."""
    while True:
        clear_screen()
        print("=== MANAGE STUDENTS ===\n")
        print("1. List/Search Students")
        print("2. Add Student")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Back\n")

        choice = input("Select option: ").strip()

        if choice == "1":
            list_students(session)
        elif choice == "2":
            add_student(session)
        elif choice == "3":
            update_student(session)
        elif choice == "4":
            delete_student(session)
        elif choice == "5":
            break
        else:
            print("⚠️ Invalid choice.")
            pause()
