"""
menus/attendants.py
Manages school bus attendants in the Transport Management System.

Now includes:
- Input validation
- Graceful error handling (no crashes)
- Safe DB rollbacks on failure
"""

from utils.helpers import pause, clear_screen, get_valid_input, confirm_action, is_phone_number
from db_models import Attendant
from sqlalchemy.orm import Session


# -----------------------------------------------------------------------------
# LIST ATTENDANTS
# -----------------------------------------------------------------------------
def list_attendants(session: Session):
    """Display all attendants currently stored in the database."""
    clear_screen()
    print("=== List of Attendants ===\n")

    attendants = session.query(Attendant).all()

    if not attendants:
        print("No attendants found.")
        pause()
        return

    for att in attendants:
        print(f"[{att.id}] {att.name}")
        print(f"  Phone: {att.phone}")
        print("-" * 30)

    pause()


# -----------------------------------------------------------------------------
# ADD ATTENDANT
# -----------------------------------------------------------------------------
def add_attendant(session: Session):
    """Create and store a new attendant record with enhanced input validation."""
    clear_screen()
    print("=== Add New Attendant ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    # Get and validate name
    name = get_valid_input("Attendant Name: ", lambda x: x.strip(), "⚠️ Name cannot be empty.")
    if name is None:
        print("Operation cancelled.")
        pause()
        return

    # Get and validate phone
    phone = get_valid_input("Phone Number: ", is_phone_number, "⚠️ Invalid phone number format.")
    if phone is None:
        print("Operation cancelled.")
        pause()
        return

    try:
        attendant = Attendant(name=name, phone=phone)
        session.add(attendant)
        session.commit()

        print("\n✅ Attendant added successfully!")

    except Exception as e:
        session.rollback()  # Revert any partial transaction
        print(f"\n❌ Error adding attendant: {e}")

    pause()


# -----------------------------------------------------------------------------
# UPDATE ATTENDANT
# -----------------------------------------------------------------------------
def update_attendant(session: Session):
    """Modify existing attendant information with enhanced validation."""
    clear_screen()
    print("=== Update Attendant ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    attendants = session.query(Attendant).all()
    if not attendants:
        print("No attendants found.")
        pause()
        return

    for att in attendants:
        print(f"[{att.id}] {att.name} ({att.phone})")

    # Get and validate attendant ID
    att_id_input = get_valid_input("\nEnter Attendant ID to update: ", lambda x: x.isdigit() and int(x) in [att.id for att in attendants], "⚠️ Invalid Attendant ID.")
    if att_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    att_id = int(att_id_input)
    attendant = session.get(Attendant, att_id)
    if not attendant:
        print("❌ Attendant not found.")
        pause()
        return

    print("\nLeave any field blank to keep existing value.\n")

    # Get and validate new name
    new_name = get_valid_input(f"New Name [{attendant.name}]: ", lambda x: x.strip() or attendant.name, "⚠️ Name cannot be empty.") or attendant.name
    if new_name is None:
        print("Operation cancelled.")
        pause()
        return
    # Get and validate new phone
    new_phone = get_valid_input(f"New Phone [{attendant.phone}]: ", is_phone_number, "⚠️ Invalid phone number format.") or attendant.phone
    if new_phone is None:
        print("Operation cancelled.")
        pause()
        return

    try:
        if new_name != attendant.name:
            attendant.name = new_name
        if new_phone != attendant.phone:
            attendant.phone = new_phone

        session.commit()
        print("\n✅ Attendant updated successfully!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error updating attendant: {e}")

    pause()


# -----------------------------------------------------------------------------
# DELETE ATTENDANT
# -----------------------------------------------------------------------------
def delete_attendant(session: Session):
    """Safely remove an attendant after explicit confirmation with enhanced validation."""
    clear_screen()
    print("=== Delete Attendant ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    attendants = session.query(Attendant).all()
    if not attendants:
        print("No attendants found.")
        pause()
        return

    for att in attendants:
        print(f"[{att.id}] {att.name} ({att.phone})")

    # Get and validate attendant ID
    att_id_input = get_valid_input("\nEnter Attendant ID to delete: ", lambda x: x.isdigit() and int(x) in [att.id for att in attendants], "⚠️ Invalid Attendant ID.")
    if att_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    att_id = int(att_id_input)
    attendant = session.get(Attendant, att_id)
    if not attendant:
        print("❌ Attendant not found.")
        pause()
        return

    # Use confirm_action for better UX
    if not confirm_action(f"delete attendant '{attendant.name}'"):
        print("❌ Deletion cancelled.")
        pause()
        return

    try:
        session.delete(attendant)
        session.commit()
        print("\n✅ Attendant deleted successfully.")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error deleting attendant: {e}")

    pause()


# -----------------------------------------------------------------------------
# ATTENDANTS MENU CONTROLLER
# -----------------------------------------------------------------------------
def attendants_menu(session: Session):
    """CLI navigation menu for managing attendants with error safety."""
    while True:
        clear_screen()
        print("--- Manage Attendants ---")
        print("1. List All Attendants")
        print("2. Add New Attendant")
        print("3. Update Attendant Info")
        print("4. Delete Attendant")
        print("5. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            list_attendants(session)
        elif choice == "2":
            add_attendant(session)
        elif choice == "3":
            update_attendant(session)
        elif choice == "4":
            delete_attendant(session)
        elif choice == "5":
            break
        else:
            print("⚠️ Invalid choice.")
            pause()
