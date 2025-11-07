"""
main.py
Entry point for the School Transport Management System (CLI version).

Handles:
- Database initialization
- Table auto-creation (safe)
- Session management
- Top-level navigation menu
"""

import sys
from sqlalchemy.orm import Session
from db_models import create_session, init_engine, DEFAULT_DB, create_all_tables  # ✅ added create_all_tables

# Import menu modules
from menus.buses import buses_menu
from menus.drivers import drivers_menu
from menus.attendants import attendants_menu
from menus.settings import settings_menu, display_day_passed_notification
from menus.students import students_menu
from menus.terms import terms_menu
from menus.academic_years import academic_years_menu
from menus.payments import payments_menu
from menus.reports import reports_menu
from utils.helpers import clear_screen, pause


# -----------------------------------------------------------------------------
# MAIN MENU
# -----------------------------------------------------------------------------
def main_menu(session: Session):
    """Displays the main navigation menu."""
    while True:
        clear_screen()
        print("=== SCHOOL TRANSPORT MANAGEMENT SYSTEM ===\n")
        print("1. Manage Buses")
        print("2. Manage Attendants")
        print("3. Manage Drivers")
        print("4. Manage Students")
        print("5. Manage Terms")
        print("6. Manage Academic Years")
        print("7. Manage Payments")
        print("8. Reports & Exports")
        print("9. Settings")
        print("10. Exit\n")

        choice = input("Select option: ").strip()

        if choice == "1":
            buses_menu(session)
        elif choice == "2":
            attendants_menu(session)
        elif choice == "3":
            drivers_menu(session)
        elif choice == "4":
            students_menu(session)
        elif choice == "5":
            terms_menu(session)
        elif choice == "6":
            academic_years_menu(session)
        elif choice == "7":
            payments_menu(session)
        elif choice == "8":
            reports_menu(session)
        elif choice == "9":
            settings_menu(session)
            pause()
        elif choice == "10":
            print("\nGoodbye!\n")
            break
        else:
            print("⚠️ Invalid option.")
            pause()


# -----------------------------------------------------------------------------
# APP ENTRY POINT
# -----------------------------------------------------------------------------
def main():
    """Initialize database and start the main menu."""
    try:
        # --- Database Setup ---
        engine = init_engine(DEFAULT_DB)

        # ✅ Ensure all tables exist (non-destructive)
        # This auto-creates any missing tables, like new models added later.
        create_all_tables(engine)

        # --- Session creation ---
        session = create_session(engine)

        # --- Check for day passed notification ---
        display_day_passed_notification(session)

        # --- Launch Main Menu ---
        main_menu(session)

    except KeyboardInterrupt:
        print("\n\nProgram interrupted. Exiting safely.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    finally:
        sys.exit(0)


# -----------------------------------------------------------------------------
# EXECUTION GUARD
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
