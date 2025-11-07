"""
menus/settings.py
Administrative settings for the Transport Management System.

Includes:
- Initialize Demo Data
- Wipe All Data
- Configure Global Settings (default transport rate, CSV export path)
- Day detection feature

All destructive actions have explicit confirmation prompts.
"""

from utils.helpers import pause, clear_screen
from sqlalchemy.orm import Session
from db_models import (
    Base, init_engine, create_session, create_all_tables,
    AcademicYear, Term, Driver, Attendant, Bus, Student, Payment
)
from db_models import SystemSetting  # <-- new model (add this to db_models.py)
from datetime import date, datetime


# -----------------------------------------------------------------------------
# SYSTEM SETTING HELPERS
# -----------------------------------------------------------------------------
def get_setting(session: Session, key: str, default=None):
    """Retrieve a system setting by key, or return default if missing."""
    setting = session.query(SystemSetting).filter_by(key=key).first()
    return setting.value if setting else default


def set_setting(session: Session, key: str, value: str):
    """Create or update a system setting (stored as string)."""
    setting = session.query(SystemSetting).filter_by(key=key).first()
    if setting:
        setting.value = str(value)
    else:
        setting = SystemSetting(key=key, value=str(value))
        session.add(setting)
    session.commit()


def check_day_passed(session: Session):
    """
    Check if a day has passed since the last run.

    Returns:
        bool: True if a day has passed, False otherwise.
    """
    last_run_str = get_setting(session, "last_run_date")
    if not last_run_str:
        # First run, set the current date
        set_setting(session, "last_run_date", str(date.today()))
        return False

    try:
        last_run_date = datetime.strptime(last_run_str, "%Y-%m-%d").date()
        current_date = date.today()
        if current_date > last_run_date:
            set_setting(session, "last_run_date", str(current_date))
            return True
        return False
    except ValueError:
        # Invalid date format, reset to current date
        set_setting(session, "last_run_date", str(date.today()))
        return False


def display_day_passed_notification(session: Session):
    """
    Display a notification if a day has passed since the last run and the feature is enabled.
    """
    # Check if day detection is enabled
    day_detection_enabled = get_setting(session, "day_detection_enabled", "true").lower() == "true"

    if day_detection_enabled and check_day_passed(session):
        clear_screen()
        print("=== Day Passed Notification ===")
        print("A day has passed since the last run of the application.")
        print("You may want to:")
        print("- Check for new payments")
        print("- Update student statuses")
        print("- Review bus assignments")
        print("\nPress Enter to continue...")
        input()


def configure_system_settings(session: Session):
    """
    Sub-menu for managing configurable system settings:
    - Default student monthly rate
    - CSV export directory path
    - Day detection feature toggle
    """
    while True:
        clear_screen()
        print("--- Configure System Settings ---\n")

        current_rate = get_setting(session, "default_monthly_rate", "Not set")
        export_path = get_setting(session, "csv_export_path", "Not set")
        day_detection_enabled = get_setting(session, "day_detection_enabled", "true").lower() == "true"

        print(f"1. Default Monthly Transport Rate: {current_rate}")
        print(f"2. CSV Export Path: {export_path}")
        print(f"3. Day Detection Feature: {'Enabled' if day_detection_enabled else 'Disabled'}")
        print("4. Back to Settings Menu\n")

        choice = input("Select an option: ").strip()

        if choice == "1":
            try:
                new_rate = float(input("Enter new default monthly rate: ").strip())
                if new_rate < 0:
                    print("❌ Rate cannot be negative.")
                else:
                    set_setting(session, "default_monthly_rate", new_rate)
                    print("✅ Default monthly rate updated successfully.")
            except ValueError:
                print("⚠️ Invalid input. Please enter a number.")
            pause()

        elif choice == "2":
            new_path = input("Enter new CSV export directory path: ").strip()
            if not new_path:
                print("⚠️ Path cannot be empty.")
            else:
                set_setting(session, "csv_export_path", new_path)
                print("✅ CSV export path updated successfully.")
            pause()

        elif choice == "3":
            current_status = "enabled" if day_detection_enabled else "disabled"
            print(f"Day detection is currently {current_status}.")
            toggle = input("Enable day detection? (y/n): ").strip().lower()
            if toggle == "y":
                set_setting(session, "day_detection_enabled", "true")
                print("✅ Day detection enabled.")
            elif toggle == "n":
                set_setting(session, "day_detection_enabled", "false")
                print("✅ Day detection disabled.")
            else:
                print("⚠️ Invalid choice.")
            pause()

        elif choice == "4":
            break

        else:
            print("⚠️ Invalid choice.")
            pause()


# -----------------------------------------------------------------------------
# DATA WIPE (SAFETY GUARDED)
# -----------------------------------------------------------------------------
def wipe_all_data(engine):
    """
    Completely removes all data and reinitializes tables.
    Useful for resetting the database without affecting schema structure.
    """
    clear_screen()
    print("⚠️  WARNING: This will delete ALL existing data permanently.")
    confirm = input("Type 'WIPE' to confirm: ").strip().upper()

    if confirm != "WIPE":
        print("\n❌ Operation cancelled. No data deleted.")
        pause()
        return

    print("\nWiping database...")
    Base.metadata.drop_all(engine)
    create_all_tables(engine)

    print("✅ All data cleared successfully.")
    pause()


# -----------------------------------------------------------------------------
# DEMO DATA INITIALIZATION
# -----------------------------------------------------------------------------
def initialize_demo_data(session: Session, engine):
    """
    Wipes all data, recreates tables, and inserts sample demo data.
    Useful for testing CLI flow and functionality.
    """
    clear_screen()
    print("⚠️  WARNING: This will delete ALL existing data and load demo data.")
    confirm = input("Are you sure you want to continue? Type 'YES' to confirm: ").strip().upper()

    if confirm != "YES":
        print("\n❌ Operation cancelled. No data was modified.")
        pause()
        return

    # Recreate database schema
    print("\nRebuilding database schema...")
    Base.metadata.drop_all(engine)
    create_all_tables(engine)

    print("Inserting demo data...")

    # === Academic year and term ===
    year = AcademicYear(name="2024/2025", start_date=date(2024, 1, 1), end_date=date(2024, 12, 31))
    term = Term(name="Term 1", start_date=date(2024, 1, 10), end_date=date(2024, 4, 5), academic_year=year)

    # === Drivers ===
    driver1 = Driver(name="John Doe", phone="0700123456", license_number="DRV001", assigned=True)
    driver2 = Driver(name="Jane Smith", phone="0700234567", license_number="DRV002", assigned=False)

    # === Attendants ===
    att1 = Attendant(name="Samuel Att", phone="0711122233")
    att2 = Attendant(name="Grace K", phone="0711223344")

    # === Buses ===
    bus1 = Bus(bus_name="Bus A", plate_number="KAA 123A", capacity=40, driver=driver1, attendant=att1)
    bus2 = Bus(bus_name="Bus B", plate_number="KBB 456B", capacity=35, driver=driver2, attendant=att2)

    # === Students ===
    s1 = Student(name="Alice Brown", parent_contact="0700998877", address="Hillview", bus=bus1, monthly_rate=50.0)
    s2 = Student(name="Brian Green", parent_contact="0700887766", address="Westlane", bus=bus2, monthly_rate=60.0)
    s3 = Student(name="Chloe White", parent_contact="0700665544", address="Eastville", bus=bus1, monthly_rate=45.0)

    # === Payments ===
    p1 = Payment(student=s1, term=term, week_number=1, amount_paid=25.0, balance_carried=25.0)
    p2 = Payment(student=s2, term=term, week_number=1, amount_paid=30.0, balance_carried=30.0)

    session.add_all([year, term, driver1, driver2, att1, att2, bus1, bus2, s1, s2, s3, p1, p2])

    # Set default settings
    set_setting(session, "default_monthly_rate", 50.0)
    set_setting(session, "csv_export_path", "exports/")
    set_setting(session, "day_detection_enabled", "true")

    session.commit()
    print("\n✅ Demo data initialized successfully!")
    pause()


# -----------------------------------------------------------------------------
# SETTINGS MENU CONTROLLER
# -----------------------------------------------------------------------------
def settings_menu(session: Session):
    """CLI interface for system administration actions."""
    engine = session.bind  # Retrieves engine from active session

    while True:
        clear_screen()
        print("--- System Settings ---")
        print("1. Initialize Demo Data (⚠️ Deletes existing data)")
        print("2. Wipe All Data (⚠️ Irreversible)")
        print("3. Configure System Settings")
        print("4. Back to Main Menu\n")

        choice = input("Select option: ").strip()

        if choice == "1":
            initialize_demo_data(session, engine)
        elif choice == "2":
            wipe_all_data(engine)
        elif choice == "3":
            configure_system_settings(session)
        elif choice == "4":
            break
        else:
            print("⚠️ Invalid option.")
            pause()
