"""
utils/helpers.py
Enhanced CLI utility functions for the School Transport Management System.

Features:
- Cross-platform screen clearing.
- User pauses with customizable messages.
- Input validation helpers (e.g., numeric, phone, email).
- Search and filtering utilities for lists.
- Confirmation prompts for critical actions.

Dependencies:
- Python's os module for system commands.
- re module for regex-based validation.

Error Handling:
- Provides fallback for invalid inputs.
- Graceful handling of system command failures.
"""

import os
import re
from datetime import datetime


def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    # Using system command for simplicity; Windows uses 'cls', Unix uses 'clear'.
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "Press Enter to continue..."):
    """Pause for user input before proceeding."""
    # Used after displaying menu results to give the user time to read.
    input(msg)


def get_valid_input(prompt: str, validation_func=None, error_msg: str = "Invalid input. Please try again."):
    """
    Get user input with optional validation and retry on errors.

    Args:
        prompt (str): The prompt message for the user.
        validation_func (callable): Optional function to validate input (should return True if valid).
        error_msg (str): Error message to display on invalid input.

    Returns:
        str: Validated user input, or None if user cancels.
    """
    while True:
        user_input = input(prompt).strip()
        if user_input.lower() in ['cancel', 'exit']:
            return None  # Allow cancellation
        if validation_func and not validation_func(user_input):
            print(error_msg)
            continue
        return user_input


def is_numeric(value: str) -> bool:
    """Check if the input is a valid number (int or float)."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def is_positive_number(value: str) -> bool:
    """Check if the input is a positive number."""
    return is_numeric(value) and float(value) > 0


def is_non_negative_number(value: str) -> bool:
    """Check if the input is a non-negative number."""
    return is_numeric(value) and float(value) >= 0


def is_integer(value: str) -> bool:
    """Check if the input is a valid integer."""
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_positive_integer(value: str) -> bool:
    """Check if the input is a positive integer."""
    return is_integer(value) and int(value) > 0


def is_non_negative_integer(value: str) -> bool:
    """Check if the input is a non-negative integer."""
    return is_integer(value) and int(value) >= 0


def is_phone_number(value: str) -> bool:
    """Check if the input is a valid phone number (basic regex for digits and common formats)."""
    # Simple regex for phone numbers: allows digits, spaces, hyphens, parentheses, and plus sign
    phone_pattern = re.compile(r'^[\+]?[0-9\s\-\(\)]+$')
    return bool(phone_pattern.match(value)) and len(value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 7


def is_email(value: str) -> bool:
    """Check if the input is a valid email address."""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(value))


def is_date(value: str) -> bool:
    """Check if the input is a valid date in YYYY-MM-DD format."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def confirm_action(action: str) -> bool:
    """
    Prompt user for confirmation of a critical action.

    Args:
        action (str): Description of the action to confirm.

    Returns:
        bool: True if user confirms, False otherwise.
    """
    response = input(f"Are you sure you want to {action}? (y/n): ").strip().lower()
    return response == "y"


def search_list(items: list, search_term: str, key_func=None) -> list:
    """
    Filter a list of items based on a search term.

    Args:
        items (list): List of items to search.
        search_term (str): Term to search for (case-insensitive).
        key_func (callable): Optional function to extract searchable text from each item.

    Returns:
        list: Filtered list of items matching the search term.
    """
    if not search_term:
        return items
    search_term = search_term.lower()
    return [item for item in items if search_term in (key_func(item).lower() if key_func else str(item).lower())]
