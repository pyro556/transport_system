"""
menus/academic_years.py
CLI menu for managing Academic Years (e.g., 2024/2025).

Each academic year defines a school year period
and acts as a container for terms (Term 1, Term 2, etc.).

Admin can:
1. View all academic years
2. Add new years
3. Edit details (like start/end dates)
4. Delete years (with confirmation)
"""

from utils.helpers import pause, clear_screen, get_valid_input, confirm_action, is_date
from db_models import AcademicYear
from datetime import datetime


# -----------------------------------------------------------------------------
# VIEW ALL ACADEMIC YEARS
# -----------------------------------------------------------------------------
def list_academic_years(session):
    """
    Displays all academic years currently stored.
    Includes their date ranges to help visualize school cycles.
    """
    clear_screen()
    years = session.query(AcademicYear).all()

    if not years:
        print("No academic years found.")
    else:
        print("--- Academic Years ---")
        for y in years:
            print(f"{y.id}. {y.name} | {y.start_date} → {y.end_date}")

    pause()


# -----------------------------------------------------------------------------
# ADD NEW ACADEMIC YEAR
# -----------------------------------------------------------------------------
def add_academic_year(session):
    """
    Adds a new academic year to the system with enhanced validation.

    The name should clearly identify the period (e.g. 2024/2025),
    and start/end dates must make logical sense (end after start).
    """
    clear_screen()
    print("--- Add Academic Year ---")
    print("Type 'cancel' at any prompt to exit.\n")

    # Basic year identification (e.g. "2024/2025")
    name = get_valid_input("Enter academic year name (e.g. 2024/2025): ", lambda x: x.strip(), "⚠️ Name cannot be empty.")
    if name is None:
        print("Operation cancelled.")
        pause()
        return

    # Date range ensures accurate reporting and linking with terms
    start_str = get_valid_input("Start date (YYYY-MM-DD): ", is_date, "⚠️ Invalid date format. Use YYYY-MM-DD.")
    if start_str is None:
        print("Operation cancelled.")
        pause()
        return
    end_str = get_valid_input("End date (YYYY-MM-DD): ", is_date, "⚠️ Invalid date format. Use YYYY-MM-DD.")
    if end_str is None:
        print("Operation cancelled.")
        pause()
        return

    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

    # Logical validation: no backwards or same-day years
    if end_date <= start_date:
        print("❌ End date must be after start date.")
        pause()
        return

    # Create & commit the new record
    year = AcademicYear(name=name, start_date=start_date, end_date=end_date)
    session.add(year)
    session.commit()

    print(f"✅ Academic year '{name}' added successfully.")
    pause()


# -----------------------------------------------------------------------------
# EDIT EXISTING ACADEMIC YEAR
# -----------------------------------------------------------------------------
def edit_academic_year(session):
    """
    Updates academic year details with enhanced validation.

    Blank inputs retain existing values, reducing risk of accidental overwrites.
    """
    clear_screen()
    print("--- Edit Academic Year ---")
    print("Type 'cancel' at any prompt to exit.\n")

    years = session.query(AcademicYear).all()

    if not years:
        print("No academic years found.")
        pause()
        return

    for y in years:
        print(f"{y.id}. {y.name} | {y.start_date} → {y.end_date}")

    # User selects the record by ID
    year_id_input = get_valid_input("\nEnter ID of year to edit: ", lambda x: x.isdigit() and int(x) in [y.id for y in years], "⚠️ Invalid Academic Year ID.")
    if year_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    year_id = int(year_id_input)
    year = session.query(AcademicYear).get(year_id)
    if not year:
        print("❌ Invalid academic year ID.")
        pause()
        return

    # Show current data to guide user
    print(f"\nEditing: {year.name} ({year.start_date} → {year.end_date})")

    # Inputs are optional — blank means "keep current"
    new_name = get_valid_input(f"New name [{year.name}]: ", lambda x: x.strip() or year.name, "⚠️ Name cannot be empty.") or year.name
    if new_name is None:
        print("Operation cancelled.")
        pause()
        return
    new_start = get_valid_input(f"New start date [{year.start_date}]: ", is_date, "⚠️ Invalid date format. Use YYYY-MM-DD.") or str(year.start_date)
    if new_start is None:
        print("Operation cancelled.")
        pause()
        return
    new_end = get_valid_input(f"New end date [{year.end_date}]: ", is_date, "⚠️ Invalid date format. Use YYYY-MM-DD.") or str(year.end_date)
    if new_end is None:
        print("Operation cancelled.")
        pause()
        return

    start_date = datetime.strptime(new_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(new_end, "%Y-%m-%d").date()

    if end_date <= start_date:
        print("❌ End date must be after start date.")
        pause()
        return

    # Save updates
    year.name, year.start_date, year.end_date = new_name, start_date, end_date
    session.commit()

    print("✅ Academic year updated successfully.")
    pause()


# -----------------------------------------------------------------------------
# DELETE AN ACADEMIC YEAR
# -----------------------------------------------------------------------------
def delete_academic_year(session):
    """
    Removes an academic year and all dependent records (if any) after confirmation.

    Since terms and payments may depend on academic years,
    this step asks for an explicit confirmation keyword.
    """
    clear_screen()
    print("--- Delete Academic Year ---")
    print("Type 'cancel' at any prompt to exit.\n")

    years = session.query(AcademicYear).all()

    if not years:
        print("No academic years available to delete.")
        pause()
        return

    for y in years:
        print(f"{y.id}. {y.name} | {y.start_date} → {y.end_date}")

    # Pick year by ID
    year_id_input = get_valid_input("\nEnter ID of year to delete: ", lambda x: x.isdigit() and int(x) in [y.id for y in years], "⚠️ Invalid Academic Year ID.")
    if year_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    year_id = int(year_id_input)
    year = session.query(AcademicYear).get(year_id)
    if not year:
        print("❌ Invalid academic year ID.")
        pause()
        return

    # Confirmation gate — prevents accidental full data loss
    if not confirm_action(f"delete academic year '{year.name}' (this may affect dependent terms and payments)"):
        print("❌ Deletion cancelled.")
        pause()
        return

    session.delete(year)
    session.commit()

    print("✅ Academic year deleted successfully.")
    pause()


# -----------------------------------------------------------------------------
# MAIN MENU CONTROLLER
# -----------------------------------------------------------------------------
def academic_years_menu(session):
    """
    The CLI controller for managing academic years.

    Provides a loop with CRUD actions and returns to main menu on exit.
    """
    while True:
        clear_screen()
        print("--- Academic Years Menu ---")
        print("1. List Academic Years")
        print("2. Add Academic Year")
        print("3. Edit Academic Year")
        print("4. Delete Academic Year")
        print("5. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        # Route to correct handler based on user input
        if choice == "1":
            list_academic_years(session)
        elif choice == "2":
            add_academic_year(session)
        elif choice == "3":
            edit_academic_year(session)
        elif choice == "4":
            delete_academic_year(session)
        elif choice == "5":
            break
        else:
            print("Invalid option.")
            pause()
