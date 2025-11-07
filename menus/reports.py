"""
menus/reports.py
Implements CLI menu for generating reports and CSV exports in the School Transport System.

Features:
- Generate reports for students (e.g., list per bus, payment summaries).
- Generate reports for payments (e.g., overdue balances, total collections per term).
- Generate reports for buses (e.g., capacity utilization, assignments).
- Export reports to CSV files for external use.
- Integrates with all models (Student, Payment, Bus, etc.) for comprehensive data.

Dependencies:
- SQLAlchemy for ORM and querying relational data.
- utils.helpers for CLI utilities (clear_screen, pause).
- db_models for all model classes and relationships.
- Python's csv module for export functionality.

Error Handling:
- Validates data availability before generating reports.
- Handles file I/O errors during CSV exports.
- Provides user-friendly messages for empty datasets.
"""

import csv
from utils.helpers import pause, clear_screen
from db_models import Student, Payment, Bus, Term, AcademicYear


# -----------------------------------------------------------------------------
# GENERATE STUDENT REPORT
# -----------------------------------------------------------------------------
def generate_student_report(session):
    """
    Generate and display a report of all students, including bus assignments and payment status.

    Displays student details like name, bus, monthly rate, and total payments made.
    Optionally exports to CSV.
    """
    clear_screen()
    print("=== Student Report ===\n")

    # Fetch students with related bus and payment data
    students = session.query(Student).all()
    if not students:
        print("No students found.")
        pause()
        return

    # Display report in console
    print("Student Report:\n")
    for student in students:
        bus_name = student.bus.bus_name if student.bus else "Unassigned"
        total_payments = sum(p.amount_paid for p in student.payments) if student.payments else 0.0
        print(f"Name: {student.name} | Bus: {bus_name} | Rate: {student.monthly_rate:.2f} | Total Paid: {total_payments:.2f}")

    # Option to export to CSV
    export = input("\nExport to CSV? (y/n): ").strip().lower()
    if export == "y":
        export_students_to_csv(students)
        print("Report exported to 'student_report.csv'.")

    pause()


# -----------------------------------------------------------------------------
# GENERATE PAYMENT REPORT
# -----------------------------------------------------------------------------
def generate_payment_report(session):
    """
    Generate and display a payment report, including overdue balances and collections per term.

    Shows payment details, balances, and summaries per term or student.
    Optionally exports to CSV.
    """
    clear_screen()
    print("=== Payment Report ===\n")

    # Fetch payments with related student and term data
    payments = session.query(Payment).join(Student).join(Term).all()
    if not payments:
        print("No payments found.")
        pause()
        return

    # Display report in console
    print("Payment Report:\n")
    total_collected = 0.0
    for payment in payments:
        student_name = payment.student.name
        term_name = payment.term.name
        print(f"Student: {student_name} | Term: {term_name} | Amount: {payment.amount_paid:.2f} | Balance: {payment.balance_carried:.2f}")
        total_collected += payment.amount_paid

    print(f"\nTotal Collected: {total_collected:.2f}")

    # Option to export to CSV
    export = input("\nExport to CSV? (y/n): ").strip().lower()
    if export == "y":
        export_payments_to_csv(payments)
        print("Report exported to 'payment_report.csv'.")

    pause()


# -----------------------------------------------------------------------------
# GENERATE BUS REPORT
# -----------------------------------------------------------------------------
def generate_bus_report(session):
    """
    Generate and display a bus utilization report, including capacity and assignments.

    Shows bus details, assigned driver/attendant, student count, and utilization percentage.
    Optionally exports to CSV.
    """
    clear_screen()
    print("=== Bus Report ===\n")

    # Fetch buses with related driver, attendant, and students
    buses = session.query(Bus).all()
    if not buses:
        print("No buses found.")
        pause()
        return

    # Display report in console
    print("Bus Report:\n")
    for bus in buses:
        driver_name = bus.driver.name if bus.driver else "Unassigned"
        attendant_name = bus.attendant.name if bus.attendant else "Unassigned"
        student_count = len(bus.students) if bus.students else 0
        utilization = (student_count / bus.capacity * 100) if bus.capacity and bus.capacity > 0 else 0
        print(f"Bus: {bus.bus_name} | Capacity: {bus.capacity} | Students: {student_count} ({utilization:.1f}%) | Driver: {driver_name} | Attendant: {attendant_name}")

    # Option to export to CSV
    export = input("\nExport to CSV? (y/n): ").strip().lower()
    if export == "y":
        export_buses_to_csv(buses)
        print("Report exported to 'bus_report.csv'.")

    pause()


# -----------------------------------------------------------------------------
# EXPORT FUNCTIONS
# -----------------------------------------------------------------------------
def export_students_to_csv(students):
    """
    Export student data to a CSV file.

    Includes fields like name, bus, rate, and total payments.
    """
    try:
        with open("student_report.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Bus", "Monthly Rate", "Total Payments"])
            for student in students:
                bus_name = student.bus.bus_name if student.bus else "Unassigned"
                total_payments = sum(p.amount_paid for p in student.payments) if student.payments else 0.0
                writer.writerow([student.name, bus_name, student.monthly_rate, total_payments])
    except IOError as e:
        print(f"Error exporting to CSV: {e}")


def export_payments_to_csv(payments):
    """
    Export payment data to a CSV file.

    Includes fields like student, term, amount, and balance.
    """
    try:
        with open("payment_report.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student", "Term", "Amount Paid", "Balance Carried"])
            for payment in payments:
                writer.writerow([payment.student.name, payment.term.name, payment.amount_paid, payment.balance_carried])
    except IOError as e:
        print(f"Error exporting to CSV: {e}")


def export_buses_to_csv(buses):
    """
    Export bus data to a CSV file.

    Includes fields like bus name, capacity, utilization, driver, and attendant.
    """
    try:
        with open("bus_report.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Bus Name", "Capacity", "Student Count", "Utilization %", "Driver", "Attendant"])
            for bus in buses:
                student_count = len(bus.students) if bus.students else 0
                utilization = (student_count / bus.capacity * 100) if bus.capacity and bus.capacity > 0 else 0
                driver_name = bus.driver.name if bus.driver else "Unassigned"
                attendant_name = bus.attendant.name if bus.attendant else "Unassigned"
                writer.writerow([bus.bus_name, bus.capacity, student_count, f"{utilization:.1f}", driver_name, attendant_name])
    except IOError as e:
        print(f"Error exporting to CSV: {e}")


# -----------------------------------------------------------------------------
# REPORTS MENU CONTROLLER
# -----------------------------------------------------------------------------
def reports_menu(session):
    """
    Main CLI navigation menu for generating reports and exports.

    Provides options to generate student, payment, bus reports, or return to main menu.
    """
    while True:
        clear_screen()
        print("--- Reports & Exports ---")
        print("1. Generate Student Report")
        print("2. Generate Payment Report")
        print("3. Generate Bus Report")
        print("4. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            generate_student_report(session)
        elif choice == "2":
            generate_payment_report(session)
        elif choice == "3":
            generate_bus_report(session)
        elif choice == "4":
            break
        else:
            print("⚠️ Invalid choice.")
            pause()
