"""
menus/buses.py
Manages school buses, each optionally linked to a driver and attendant.

Includes:
- Input validation for numeric and text fields
- Safe database commits with rollback on error
- Delete confirmation before data removal
"""

from utils.helpers import pause, clear_screen, get_valid_input, confirm_action, is_non_negative_integer
from db_models import Bus, Driver, Attendant
from sqlalchemy.orm import Session


# -----------------------------------------------------------------------------
# LIST BUSES
# -----------------------------------------------------------------------------
def list_buses(session: Session):
    """Display all buses with assigned driver, attendant, and seat utilization."""
    clear_screen()
    print("=== List of Buses ===\n")

    buses = session.query(Bus).all()
    if not buses:
        print("No buses found.")
        pause()
        return

    for bus in buses:
        driver_name = bus.driver.name if bus.driver else "—"
        attendant_name = bus.attendant.name if bus.attendant else "—"
        student_count = len(bus.students) if bus.students else 0
        utilization = (student_count / bus.capacity * 100) if bus.capacity and bus.capacity > 0 else 0

        print(f"[{bus.id}] {bus.bus_name}")
        print(f"  Seats: {student_count}/{bus.capacity} filled ({utilization:.1f}%)")
        print(f"  Driver: {driver_name}")
        print(f"  Attendant: {attendant_name}")
        print("-" * 50)

    pause()


# -----------------------------------------------------------------------------
# ADD BUS
# -----------------------------------------------------------------------------
def add_bus(session: Session):
    """Create and store a new bus with enhanced validation."""
    clear_screen()
    print("=== Add New Bus ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    # Get and validate bus name
    name = get_valid_input("Bus Name: ", lambda x: x.strip(), "⚠️ Bus name cannot be empty.")
    if name is None:
        print("Operation cancelled.")
        pause()
        return

    # Get and validate capacity
    capacity_input = get_valid_input("Capacity: ", is_non_negative_integer, "⚠️ Capacity must be a non-negative integer.")
    if capacity_input is None:
        print("Operation cancelled.")
        pause()
        return
    capacity = int(capacity_input)

    # Optional driver
    print("\nAvailable Drivers:")
    drivers = session.query(Driver).all()
    if drivers:
        for d in drivers:
            print(f"[{d.id}] {d.name}")
        driver_id_input = get_valid_input("Assign Driver ID (or leave blank): ", lambda x: not x or (x.isdigit() and int(x) in [d.id for d in drivers]), "⚠️ Invalid Driver ID.")
        if driver_id_input is None:
            print("Operation cancelled.")
            pause()
            return
        driver = session.get(Driver, int(driver_id_input)) if driver_id_input else None
    else:
        print("No drivers available.")
        driver = None

    # Optional attendant
    print("\nAvailable Attendants:")
    attendants = session.query(Attendant).all()
    if attendants:
        for a in attendants:
            print(f"[{a.id}] {a.name}")
        attendant_id_input = get_valid_input("Assign Attendant ID (or leave blank): ", lambda x: not x or (x.isdigit() and int(x) in [a.id for a in attendants]), "⚠️ Invalid Attendant ID.")
        if attendant_id_input is None:
            print("Operation cancelled.")
            pause()
            return
        attendant = session.get(Attendant, int(attendant_id_input)) if attendant_id_input else None
    else:
        print("No attendants available.")
        attendant = None

    try:
        new_bus = Bus(bus_name=name, capacity=capacity, driver=driver, attendant=attendant)
        session.add(new_bus)
        session.commit()

        print("\n✅ Bus added successfully!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error adding bus: {e}")

    pause()


# -----------------------------------------------------------------------------
# UPDATE BUS
# -----------------------------------------------------------------------------
def update_bus(session: Session):
    """Modify existing bus info with enhanced validation."""
    clear_screen()
    print("=== Update Bus ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    buses = session.query(Bus).all()
    if not buses:
        print("No buses found.")
        pause()
        return

    for b in buses:
        student_count = len(b.students) if b.students else 0
        print(f"[{b.id}] {b.bus_name} (Seats: {student_count}/{b.capacity} filled)")

    # Get and validate bus ID
    bus_id_input = get_valid_input("\nEnter Bus ID to update: ", lambda x: x.isdigit() and int(x) in [b.id for b in buses], "⚠️ Invalid Bus ID.")
    if bus_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    bus_id = int(bus_id_input)
    bus = session.get(Bus, bus_id)
    if not bus:
        print("❌ Bus not found.")
        pause()
        return

    print("\nLeave fields blank to keep current values.\n")

    # Get and validate new name
    new_name = get_valid_input(f"New Name [{bus.bus_name}]: ", lambda x: x.strip() or bus.bus_name, "⚠️ Name cannot be empty.") or bus.bus_name
    if new_name is None:
        print("Operation cancelled.")
        pause()
        return
    # Get and validate new capacity
    new_capacity_input = get_valid_input(f"New Capacity [{bus.capacity}]: ", is_non_negative_integer, "⚠️ Capacity must be a non-negative integer.")
    if new_capacity_input is None:
        print("Operation cancelled.")
        pause()
        return
    new_capacity = int(new_capacity_input) if new_capacity_input else bus.capacity

    try:
        if new_name != bus.bus_name:
            bus.bus_name = new_name
        if new_capacity != bus.capacity:
            bus.capacity = new_capacity

        # Optionally reassign driver/attendant
        print("\nReassign Driver (leave blank to skip):")
        drivers = session.query(Driver).all()
        if drivers:
            for d in drivers:
                print(f"[{d.id}] {d.name}")
            driver_id_input = get_valid_input("New Driver ID (or blank): ", lambda x: not x or (x.isdigit() and int(x) in [d.id for d in drivers]), "⚠️ Invalid Driver ID.")
            if driver_id_input is None:
                print("Operation cancelled.")
                pause()
                return
            bus.driver = session.get(Driver, int(driver_id_input)) if driver_id_input else bus.driver
        else:
            print("No drivers available.")

        print("\nReassign Attendant (leave blank to skip):")
        attendants = session.query(Attendant).all()
        if attendants:
            for a in attendants:
                print(f"[{a.id}] {a.name}")
            attendant_id_input = get_valid_input("New Attendant ID (or blank): ", lambda x: not x or (x.isdigit() and int(x) in [a.id for a in attendants]), "⚠️ Invalid Attendant ID.")
            if attendant_id_input is None:
                print("Operation cancelled.")
                pause()
                return
            bus.attendant = session.get(Attendant, int(attendant_id_input)) if attendant_id_input else bus.attendant
        else:
            print("No attendants available.")

        session.commit()
        print("\n✅ Bus updated successfully!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error updating bus: {e}")

    pause()


# -----------------------------------------------------------------------------
# DELETE BUS
# -----------------------------------------------------------------------------
def delete_bus(session: Session):
    """Safely remove a bus record after confirmation with enhanced validation."""
    clear_screen()
    print("=== Delete Bus ===\n")
    print("Type 'cancel' at any prompt to exit.\n")

    buses = session.query(Bus).all()
    if not buses:
        print("No buses found.")
        pause()
        return

    for b in buses:
        print(f"[{b.id}] {b.bus_name}")

    # Get and validate bus ID
    bus_id_input = get_valid_input("\nEnter Bus ID to delete: ", lambda x: x.isdigit() and int(x) in [b.id for b in buses], "⚠️ Invalid Bus ID.")
    if bus_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    bus_id = int(bus_id_input)
    bus = session.get(Bus, bus_id)
    if not bus:
        print("❌ Bus not found.")
        pause()
        return

    # Use confirm_action for better UX
    if not confirm_action(f"delete bus '{bus.bus_name}' (this may affect assigned students)"):
        print("❌ Deletion cancelled.")
        pause()
        return

    try:
        session.delete(bus)
        session.commit()
        print("\n✅ Bus deleted successfully.")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error deleting bus: {e}")

    pause()


# -----------------------------------------------------------------------------
# BUSES MENU CONTROLLER
# -----------------------------------------------------------------------------
def buses_menu(session: Session):
    """CLI navigation menu for managing buses safely."""
    while True:
        clear_screen()
        print("--- Manage Buses ---")
        print("1. List All Buses")
        print("2. Add New Bus")
        print("3. Update Bus Info")
        print("4. Delete Bus")
        print("5. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            list_buses(session)
        elif choice == "2":
            add_bus(session)
        elif choice == "3":
            update_bus(session)
        elif choice == "4":
            delete_bus(session)
        elif choice == "5":
            break
        else:
            print("⚠️ Invalid choice.")
            pause()
