"""
menus/terms.py
Manages school terms (e.g., Term 1, Term 2) linked to academic years.

This CLI menu allows the admin to:
1. View all terms with their academic year context.
2. Add new terms (requires an academic year).
3. Edit existing terms (with validation and optional reassignment).
4. Delete terms (with confirmation to prevent accidental loss).
"""

from utils.helpers import pause, clear_screen, get_valid_input, confirm_action, is_date
from db_models import Term, AcademicYear
from datetime import datetime


# -----------------------------------------------------------------------------
# VIEW ALL TERMS
# -----------------------------------------------------------------------------
def list_terms(session):
    """
    Displays all terms in the database, including their academic year.
    Useful for overview before editing or deleting.
    """
    clear_screen()
    terms = session.query(Term).all()

    if not terms:
        print("No terms found.")
    else:
        print("--- School Terms ---")
        for t in terms:
            # Show both the date range and linked academic year
            print(f"{t.id}. {t.name} | {t.start_date} → {t.end_date} | Year: {t.academic_year.name}")

    pause()


# -----------------------------------------------------------------------------
# ADD NEW TERM
# -----------------------------------------------------------------------------
def add_term(session):
    """
    Adds a new school term (e.g., Term 1) under a selected academic year with enhanced validation.
    Input validation ensures correct date formatting and logical date order.
    """
    clear_screen()
    print("--- Add Term ---")
    print("Type 'cancel' at any prompt to exit.\n")

    # Must have at least one academic year before adding terms
    years = session.query(AcademicYear).all()
    if not years:
        print("❌ No academic years found. Please add one first.")
        pause()
        return

    # Show available academic years for user to choose from
    print("Select Academic Year:")
    for y in years:
        print(f"{y.id}. {y.name}")

    # Validate chosen year
    year_id_input = get_valid_input("Enter Year ID: ", lambda x: x.isdigit() and int(x) in [y.id for y in years], "⚠️ Invalid Academic Year ID.")
    if year_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    year_id = int(year_id_input)
    year = session.query(AcademicYear).get(year_id)
    if not year:
        print("❌ Invalid academic year selected.")
        pause()
        return

    # Gather basic term info
    name = get_valid_input("Enter term name (e.g. Term 1): ", lambda x: x.strip(), "⚠️ Name cannot be empty.")
    if name is None:
        print("Operation cancelled.")
        pause()
        return

    # Collect and validate start/end dates
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

    # Convert strings → datetime.date objects
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

    # Validate date logic
    if end_date <= start_date:
        print("❌ End date must be after start date.")
        pause()
        return

    # Create and persist new term record
    term = Term(name=name, start_date=start_date, end_date=end_date, academic_year=year)
    session.add(term)
    session.commit()

    print(f"✅ {name} added successfully under {year.name}.")
    pause()


# -----------------------------------------------------------------------------
# EDIT EXISTING TERM
# -----------------------------------------------------------------------------
def edit_term(session):
    """
    Updates term details like name, start/end dates, or assigned academic year with enhanced validation.
    Includes non-destructive editing: keeps old values if left blank.
    """
    clear_screen()
    print("--- Edit Term ---")
    print("Type 'cancel' at any prompt to exit.\n")

    terms = session.query(Term).all()

    if not terms:
        print("No terms available to edit.")
        pause()
        return

    for t in terms:
        print(f"{t.id}. {t.name} | {t.academic_year.name} | {t.start_date} → {t.end_date}")

    # Prompt for ID of term to edit
    term_id_input = get_valid_input("\nEnter ID of term to edit: ", lambda x: x.isdigit() and int(x) in [t.id for t in terms], "⚠️ Invalid Term ID.")
    if term_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    term_id = int(term_id_input)
    term = session.query(Term).get(term_id)
    if not term:
        print("❌ Invalid term ID.")
        pause()
        return

    # Show existing details for reference
    print(f"\nEditing: {term.name} ({term.academic_year.name})")

    # Allow blank inputs → retain old value
    new_name = get_valid_input(f"New name [{term.name}]: ", lambda x: x.strip() or term.name, "⚠️ Name cannot be empty.") or term.name
    if new_name is None:
        print("Operation cancelled.")
        pause()
        return
    new_start = get_valid_input(f"New start date [{term.start_date}]: ", is_date, "⚠️ Invalid date format. Use YYYY-MM-DD.") or str(term.start_date)
    if new_start is None:
        print("Operation cancelled.")
        pause()
        return
    new_end = get_valid_input(f"New end date [{term.end_date}]: ", is_date, "⚠️ Invalid date format. Use YYYY-MM-DD.") or str(term.end_date)
    if new_end is None:
        print("Operation cancelled.")
        pause()
        return

    # Validate date formats and order
    start_date = datetime.strptime(new_start, "%Y-%m-%d").date()
    end_date = datetime.strptime(new_end, "%Y-%m-%d").date()

    if end_date <= start_date:
        print("❌ End date must be after start date.")
        pause()
        return

    # Optional reassignment to another academic year
    reassign = get_valid_input("Change academic year? (y/N): ", lambda x: x.lower() in ['y', 'n', ''], "⚠️ Please enter 'y' or 'n'.")
    if reassign is None:
        print("Operation cancelled.")
        pause()
        return
    if reassign.lower() == "y":
        years = session.query(AcademicYear).all()
        for y in years:
            print(f"{y.id}. {y.name}")
        year_id_input = get_valid_input("Enter new academic year ID: ", lambda x: x.isdigit() and int(x) in [y.id for y in years], "⚠️ Invalid Academic Year ID.")
        if year_id_input is None:
            print("Operation cancelled.")
            pause()
            return
        year_id = int(year_id_input)
        new_year = session.query(AcademicYear).get(year_id)
        if not new_year:
            print("❌ Invalid academic year ID.")
            pause()
            return
        term.academic_year = new_year

    # Apply final updates
    term.name, term.start_date, term.end_date = new_name, start_date, end_date
    session.commit()

    print("✅ Term updated successfully.")
    pause()


# -----------------------------------------------------------------------------
# DELETE TERM
# -----------------------------------------------------------------------------
def delete_term(session):
    """
    Permanently removes a term record after explicit confirmation with enhanced validation.
    Uses a strong confirmation keyword ("DELETE") to avoid accidental loss.
    """
    clear_screen()
    print("--- Delete Term ---")
    print("Type 'cancel' at any prompt to exit.\n")

    terms = session.query(Term).all()

    if not terms:
        print("No terms available to delete.")
        pause()
        return

    for t in terms:
        print(f"{t.id}. {t.name} | {t.academic_year.name} | {t.start_date} → {t.end_date}")

    # Pick term by ID
    term_id_input = get_valid_input("\nEnter ID of term to delete: ", lambda x: x.isdigit() and int(x) in [t.id for t in terms], "⚠️ Invalid Term ID.")
    if term_id_input is None:
        print("Operation cancelled.")
        pause()
        return
    term_id = int(term_id_input)
    term = session.query(Term).get(term_id)
    if not term:
        print("❌ Invalid term ID.")
        pause()
        return

    # Explicit confirmation — avoids unintended data loss
    if not confirm_action(f"delete term '{term.name}' (this may affect dependent payments)"):
        print("❌ Deletion cancelled.")
        pause()
        return

    session.delete(term)
    session.commit()
    print("✅ Term deleted successfully.")
    pause()


# -----------------------------------------------------------------------------
# MAIN MENU CONTROLLER
# -----------------------------------------------------------------------------
def terms_menu(session):
    """
    The main controller function for managing school terms.

    Provides a CLI loop where the user can:
    - View terms
    - Add new ones
    - Edit or delete existing terms
    - Return to the main menu

    The loop only exits when option '5' is chosen.
    """
    while True:
        clear_screen()
        print("--- Terms Menu ---")
        print("1. List Terms")
        print("2. Add Term")
        print("3. Edit Term")
        print("4. Delete Term")
        print("5. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            list_terms(session)
        elif choice == "2":
            add_term(session)
        elif choice == "3":
            edit_term(session)
        elif choice == "4":
            delete_term(session)
        elif choice == "5":
            break
        else:
            print("Invalid option.")
            pause()
