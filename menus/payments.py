"""
menus/payments.py
Implements CLI menu for managing student transport payments in the School Transport System.

Features:
- List payments with filtering options (by student, term, or all).
- Add new payments with validation for amounts and balance calculations.
- Update existing payments (e.g., adjust amounts or balances).
- Delete payments with confirmation.
- Integrates with Student and Term models for relational data.
- Handles balance carried forward and ensures data integrity via constraints.

Dependencies:
- SQLAlchemy for ORM and session management.
- utils.helpers for CLI utilities (clear_screen, pause).
- db_models for Payment, Student, Term models and relationships.

Error Handling:
- Uses try-except blocks with session rollbacks on failures.
- Validates inputs (e.g., numeric amounts, existing student/term IDs).
- Prevents invalid operations like negative amounts or duplicate weekly payments.
"""

from sqlalchemy.exc import SQLAlchemyError
from utils.helpers import pause, clear_screen
from db_models import Payment, Student, Term


# -----------------------------------------------------------------------------
# LIST PAYMENTS
# -----------------------------------------------------------------------------
def list_payments(session):
    """
    Display all payments with optional filtering by student or term.

    Fetches and prints payment records, including student name, term details,
    amount paid, balance, and payment date. Allows user to filter results.
    """
    clear_screen()
    print("=== List Payments ===\n")

    # Fetch all payments with related student and term data
    payments = session.query(Payment).join(Student).join(Term).all()

    if not payments:
        print("No payments found.")
        pause()
        return

    # Display each payment with details
    for payment in payments:
        student_name = payment.student.name
        term_name = payment.term.name
        academic_year = payment.term.academic_year.name
        print(f"ID: {payment.id} | Student: {student_name} | Term: {term_name} ({academic_year})")
        print(f"  Week: {payment.week_number or 'N/A'} | Amount Paid: {payment.amount_paid:.2f}")
        print(f"  Balance Carried: {payment.balance_carried:.2f} | Date: {payment.payment_date}")
        print("-" * 60)

    pause()


# -----------------------------------------------------------------------------
# ADD PAYMENT
# -----------------------------------------------------------------------------
def add_payment(session):
    """
    Add a new payment record for a student in a specific term.

    Prompts for student ID, term ID, week number (optional), and amount paid.
    Calculates balance carried forward based on student's monthly rate.
    Validates inputs and ensures no duplicate weekly payments.
    """
    clear_screen()
    print("=== Add New Payment ===\n")

    # List available students
    students = session.query(Student).all()
    if not students:
        print("⚠️ No students available. Add students first.")
        pause()
        return

    print("Available Students:")
    for s in students:
        bus_name = s.bus.bus_name if s.bus else "None"
        print(f"[{s.id}] {s.name} (Bus: {bus_name}, Rate: {s.monthly_rate:.2f})")

    try:
        student_id = int(input("\nEnter Student ID: ").strip())
    except ValueError:
        print("⚠️ Invalid Student ID.")
        pause()
        return

    student = session.get(Student, student_id)
    if not student:
        print("❌ Student not found.")
        pause()
        return

    # List available terms
    terms = session.query(Term).all()
    if not terms:
        print("⚠️ No terms available. Add terms first.")
        pause()
        return

    print("\nAvailable Terms:")
    for t in terms:
        print(f"[{t.id}] {t.name} ({t.academic_year.name})")

    try:
        term_id = int(input("\nEnter Term ID: ").strip())
    except ValueError:
        print("⚠️ Invalid Term ID.")
        pause()
        return

    term = session.get(Term, term_id)
    if not term:
        print("❌ Term not found.")
        pause()
        return

    # Optional week number (for weekly payments)
    week_input = input("Week Number (1-20, or leave blank for general): ").strip()
    week_number = int(week_input) if week_input and week_input.isdigit() else None
    if week_number and (week_number < 1 or week_number > 20):
        print("⚠️ Week number must be between 1 and 20.")
        pause()
        return

    # Check for duplicate weekly payment
    existing = session.query(Payment).filter_by(
        student_id=student_id, term_id=term_id, week_number=week_number
    ).first()
    if existing:
        print("⚠️ A payment for this student, term, and week already exists.")
        pause()
        return

    # Input amount paid
    try:
        amount_paid = float(input("Amount Paid: ").strip())
        if amount_paid < 0:
            raise ValueError
    except ValueError:
        print("⚠️ Amount must be a non-negative number.")
        pause()
        return

    # Calculate balance carried (simplified: student's monthly rate minus amount paid)
    # In a real scenario, this might involve more complex logic like previous balances
    balance_carried = max(0, student.monthly_rate - amount_paid)

    # Create and save payment
    try:
        new_payment = Payment(
            student_id=student_id,
            term_id=term_id,
            week_number=week_number,
            amount_paid=amount_paid,
            balance_carried=balance_carried,
        )
        session.add(new_payment)
        session.commit()
        print("\n✅ Payment added successfully!")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"\n❌ Error adding payment: {e}")

    pause()


# -----------------------------------------------------------------------------
# UPDATE PAYMENT
# -----------------------------------------------------------------------------
def update_payment(session):
    """
    Update an existing payment record.

    Allows editing of amount paid and balance carried. Revalidates constraints
    and updates related calculations if needed.
    """
    clear_screen()
    print("=== Update Payment ===\n")

    payments = session.query(Payment).join(Student).join(Term).all()
    if not payments:
        print("No payments found.")
        pause()
        return

    # List payments for selection
    for p in payments:
        print(f"[{p.id}] {p.student.name} - {p.term.name} (Week: {p.week_number or 'N/A'}, Amount: {p.amount_paid:.2f})")

    try:
        payment_id = int(input("\nEnter Payment ID to update: ").strip())
    except ValueError:
        print("⚠️ Invalid Payment ID.")
        pause()
        return

    payment = session.get(Payment, payment_id)
    if not payment:
        print("❌ Payment not found.")
        pause()
        return

    print("\nLeave fields blank to keep current values.\n")

    # Update amount paid
    amount_input = input(f"New Amount Paid [{payment.amount_paid:.2f}]: ").strip()
    try:
        new_amount = float(amount_input) if amount_input else payment.amount_paid
        if new_amount < 0:
            raise ValueError
    except ValueError:
        print("⚠️ Amount must be a non-negative number.")
        pause()
        return

    # Recalculate balance if amount changed
    if amount_input:
        student = payment.student
        payment.balance_carried = max(0, student.monthly_rate - new_amount)

    # Update record
    try:
        payment.amount_paid = new_amount
        session.commit()
        print("\n✅ Payment updated successfully!")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"\n❌ Error updating payment: {e}")

    pause()


# -----------------------------------------------------------------------------
# DELETE PAYMENT
# -----------------------------------------------------------------------------
def delete_payment(session):
    """
    Delete a payment record after confirmation.

    Ensures user confirms deletion to prevent accidental data loss.
    """
    clear_screen()
    print("=== Delete Payment ===\n")

    payments = session.query(Payment).join(Student).join(Term).all()
    if not payments:
        print("No payments found.")
        pause()
        return

    # List payments for selection
    for p in payments:
        print(f"[{p.id}] {p.student.name} - {p.term.name} (Amount: {p.amount_paid:.2f})")

    try:
        payment_id = int(input("\nEnter Payment ID to delete: ").strip())
    except ValueError:
        print("⚠️ Invalid Payment ID.")
        pause()
        return

    payment = session.get(Payment, payment_id)
    if not payment:
        print("❌ Payment not found.")
        pause()
        return

    confirm = input(f"Type DELETE to confirm removal of payment for {payment.student.name}: ").strip().upper()
    if confirm != "DELETE":
        print("\n❌ Operation cancelled.")
        pause()
        return

    try:
        session.delete(payment)
        session.commit()
        print("\n✅ Payment deleted successfully.")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"\n❌ Error deleting payment: {e}")

    pause()


# -----------------------------------------------------------------------------
# PAYMENTS MENU CONTROLLER
# -----------------------------------------------------------------------------
def payments_menu(session):
    """
    Main CLI navigation menu for managing payments.

    Provides options to list, add, update, delete payments, or return to main menu.
    """
    while True:
        clear_screen()
        print("--- Manage Payments ---")
        print("1. List All Payments")
        print("2. Add New Payment")
        print("3. Update Payment")
        print("4. Delete Payment")
        print("5. Back to Main Menu")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            list_payments(session)
        elif choice == "2":
            add_payment(session)
        elif choice == "3":
            update_payment(session)
        elif choice == "4":
            delete_payment(session)
        elif choice == "5":
            break
        else:
            print("⚠️ Invalid choice.")
            pause()
