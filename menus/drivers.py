"""
menus/drivers.py
Handles CRUD operations for bus drivers in the Transport Management System.

Includes:
- Input validation (no blanks, numeric ID checks)
- Graceful exception handling
- Rollback protection for failed DB writes
- Delete confirmation prompt
"""

from utils.helpers import pause, clear_screen, get_valid_input, confirm_action, is_phone_number
from db_models import Driver
from sqlalchemy.orm import Session


# -----------------------------------------------------------------------------
# LIST DRIVERS
# -----------------------------------------------------------------------------
def list_drivers(session: Session):
    """Display all registered drivers."""
    clear_screen()
    print("=== List of Drivers ===\n")

    drivers = session.query(Driver).all()
    if not drivers:
        print("No drivers found.")
        pause()
        return

    for d in drivers:
        print(f"[{d.id}] {d.name}")
        print(f"  Phone: {d.phone}")
        print(f"  License No: {d.license_number}")
        print("-" * 30)

    pause()


# -----------------------------------------------------------------------------
# ADD DRIVER
# -----------------------------------------------------------------------------
def add_driver(session: Session):
    """Create and store a new driver record with enhanced validation."""
    clear_screen()
    print("=== Add New Driver ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    # Get and validate name
    name = get_valid_input("Driver Name: ", lambda x: x.strip(), "⚠️ Name cannot be empty.")
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

    # Get and validate license number
    license_no = get_valid_input("License Number: ", lambda x: x.strip(), "⚠️ License number cannot be empty.")
    if license_no is None:
        print("Operation cancelled.")
        pause()
        return

    try:
        driver = Driver(name=name, phone=phone, license_number=license_no)
        session.add(driver)
        session.commit()

        print("\n✅ Driver added successfully!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error adding driver: {e}")

    pause()


# -----------------------------------------------------------------------------
# UPDATE DRIVER
# -----------------------------------------------------------------------------
def update_driver(session: Session):
    """Safely modify existing driver details with enhanced validation."""
    clear_screen()
    print("=== Update Driver ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    drivers = session.query(Driver).all()
    if not drivers:
        print("No drivers found.")
        pause()
        return

    for d in drivers:
        print(f"[{d.id}] {d.name} ({d.phone}) - License: {d.license_number}")

    # Get and validate driver ID
    driver_id_input = get_valid_input("\nEnter Driver ID to update: ", lambda x: x.isdigit() and int(x) in [d.id for d in drivers], "⚠️ Invalid Driver ID.")
    if driver_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    driver_id = int(driver_id_input)
    driver = session.get(Driver, driver_id)
    if not driver:
        print("❌ Driver not found.")
        pause()
        return

    print("\nLeave any field blank to keep existing value.\n")

    # Get and validate new name
    new_name = get_valid_input(f"New Name [{driver.name}]: ", lambda x: x.strip() or driver.name, "⚠️ Name cannot be empty.") or driver.name
    if new_name is None:
        print("Operation cancelled.")
        pause()
        return
    # Get and validate new phone
    new_phone = get_valid_input(f"New Phone [{driver.phone}]: ", is_phone_number, "⚠️ Invalid phone number format.") or driver.phone
    if new_phone is None:
        print("Operation cancelled.")
        pause()
        return
    # Get and validate new license number
    new_license = get_valid_input(f"New License No [{driver.license_number}]: ", lambda x: x.strip() or driver.license_number, "⚠️ License number cannot be empty.") or driver.license_number
    if new_license is None:
        print("Operation cancelled.")
        pause()
        return

    try:
        if new_name != driver.name:
            driver.name = new_name
        if new_phone != driver.phone:
            driver.phone = new_phone
        if new_license != driver.license_number:
            driver.license_number = new_license

        session.commit()
        print("\n✅ Driver updated successfully!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error updating driver: {e}")

    pause()


# -----------------------------------------------------------------------------
# DELETE DRIVER
# -----------------------------------------------------------------------------
def delete_driver(session: Session):
    """Safely remove a driver after explicit confirmation with enhanced validation."""
    clear_screen()
    print("=== Delete Driver ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    drivers = session.query(Driver).all()
    if not drivers:
        print("No drivers found.")
        pause()
        return

    for d in drivers:
        print(f"[{d.id}] {d.name} ({d.phone})")

    # Get and validate driver ID
    driver_id_input = get_valid_input("\nEnter Driver ID to delete: ", lambda x: x.isdigit() and int(x) in [d.id for d in drivers], "⚠️ Invalid Driver ID.")
    if driver_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    driver_id = int(driver_id_input)
    driver = session.get(Driver, driver_id)
    if not driver:
        print("❌ Driver not found.")
        pause()
        return

    # Use confirm_action for better UX
    if not confirm_action(f"delete driver '{driver.name}'"):
        print("❌ Deletion cancelled.")
        pause()
        return

    try:
        session.delete(driver)
        session.commit()
        print("\n✅ Driver deleted successfully.")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error deleting driver: {e}")

    pause()


# -----------------------------------------------------------------------------
# DRIVERS MENU CONTROLLER
# -----------------------------------------------------------------------------
def drivers_menu(session: Session):
    """CLI navigation menu for managing drivers safely."""
    while True:
        clear_screen()
        print("--- Manage Drivers ---")
        print("1. List All Drivers")
        print("2. Add New Driver")
        print("3. Update Driver Info")
        print("4. Delete Driver")
        print("5. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            list_drivers(session)
        elif choice == "2":
            add_driver(session)
        elif choice == "3":
            update_driver(session)
        elif choice == "4":
            delete_driver(session)
        elif choice == "5":
            break
        else:
            print("⚠️ Invalid choice.")
            pause()
