import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk


class ContactApp:
    """Desktop CRUD application for managing contacts with SQLite storage."""

    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("700x450")
        self.root.resizable(False, False)

        # Create or open the SQLite database and initialize the table
        self.db_connection = sqlite3.connect("contacts.db")
        self.db_cursor = self.db_connection.cursor()
        self.create_table()

        # GUI elements
        self.create_widgets()
        self.load_contacts()

    def create_table(self):
        """Create the contacts table if it does not already exist."""
        self.db_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT
            )
            """
        )
        self.db_connection.commit()

    