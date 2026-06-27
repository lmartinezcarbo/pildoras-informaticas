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

    def create_widgets(self):
        """Build and layout the user interface components."""
        # Input fields frame
        form_frame = ttk.LabelFrame(self.root, text="Contact Details")
        form_frame.place(x=20, y=20, width=660, height=170)

        # Name field
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        # Email field
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(form_frame, textvariable=self.email_var, width=30)
        self.email_entry.grid(row=1, column=1, padx=10, pady=10)

        # Phone field
        ttk.Label(form_frame, text="Phone:").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(form_frame, textvariable=self.phone_var, width=30)
        self.phone_entry.grid(row=0, column=3, padx=10, pady=10)

        # Address field
        ttk.Label(form_frame, text="Address:").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.address_var = tk.StringVar()
        self.address_entry = ttk.Entry(form_frame, textvariable=self.address_var, width=30)
        self.address_entry.grid(row=1, column=3, padx=10, pady=10)

        # Button frame for CRUD actions
        button_frame = ttk.Frame(self.root)
        button_frame.place(x=20, y=200, width=660, height=60)

        ttk.Button(button_frame, text="Add Contact", command=self.add_contact).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Update Contact", command=self.update_contact).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Delete Contact", command=self.delete_contact).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_form).grid(row=0, column=3, padx=10)

        # Contact list display using Treeview
        self.contacts_tree = ttk.Treeview(self.root, columns=("Name", "Email", "Phone", "Address"), show="headings")
        self.contacts_tree.heading("Name", text="Name")
        self.contacts_tree.heading("Email", text="Email")
        self.contacts_tree.heading("Phone", text="Phone")
        self.contacts_tree.heading("Address", text="Address")
        self.contacts_tree.column("Name", width=150)
        self.contacts_tree.column("Email", width=170)
        self.contacts_tree.column("Phone", width=120)
        self.contacts_tree.column("Address", width=200)
        self.contacts_tree.place(x=20, y=280, width=660, height=150)
        self.contacts_tree.bind("<ButtonRelease-1>", self.on_row_select)

        # Status label at bottom
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="blue")
        self.status_label.place(x=20, y=420)

    def load_contacts(self):
        """Fetch contacts from the database and display them in the Treeview."""
        for row in self.contacts_tree.get_children():
            self.contacts_tree.delete(row)

        self.db_cursor.execute("SELECT id, name, email, phone, address FROM contacts ORDER BY name")
        rows = self.db_cursor.fetchall()

        for contact in rows:
            self.contacts_tree.insert("", tk.END, iid=contact[0], values=contact[1:])

        self.set_status(f"Loaded {len(rows)} contacts.")

    def validate_form(self):
        """Check that mandatory fields are filled in before database operations."""
        if not self.name_var.get().strip():
            messagebox.showwarning("Validation Error", "Name is required.")
            return False
        if not self.email_var.get().strip():
            messagebox.showwarning("Validation Error", "Email is required.")
            return False
        if not self.phone_var.get().strip():
            messagebox.showwarning("Validation Error", "Phone is required.")
            return False
        return True

    def add_contact(self):
        """Insert a new contact into the SQLite database."""
        if not self.validate_form():
            return

        self.db_cursor.execute(
            "INSERT INTO contacts (name, email, phone, address) VALUES (?, ?, ?, ?)",
            (self.name_var.get().strip(), self.email_var.get().strip(), self.phone_var.get().strip(), self.address_var.get().strip()),
        )
        self.db_connection.commit()
        self.load_contacts()
        self.clear_form()
        self.set_status("Contact added successfully.")

    def update_contact(self):
        """Update the selected contact record in the database."""
        selected = self.contacts_tree.selection()
        if not selected:
            messagebox.showinfo("Update Contact", "Select a contact to update.")
            return

        if not self.validate_form():
            return
        contact_id = selected[0]
        self.db_cursor.execute(
            "UPDATE contacts SET name = ?, email = ?, phone = ?, address = ? WHERE id = ?",
            (self.name_var.get().strip(), self.email_var.get().strip(), self.phone_var.get().strip(), self.address_var.get().strip(), contact_id),
        )
        self.db_connection.commit()
        self.load_contacts()
        self.set_status("Contact updated successfully.")

    def delete_contact(self):
        """Remove the selected contact from the database."""
        selected = self.contacts_tree.selection()
        if not selected:
            messagebox.showinfo("Delete Contact", "Select a contact to delete.")
            return

        result = messagebox.askyesno("Delete Contact", "Are you sure you want to delete this contact?")
        if not result:
            return

        contact_id = selected[0]
        self.db_cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.db_connection.commit()
        self.load_contacts()
        self.clear_form()
        self.set_status("Contact deleted successfully.")

    def clear_form(self):
        """Reset the input fields so the user can add a new contact."""
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.contacts_tree.selection_remove(self.contacts_tree.selection())
        self.set_status("Form cleared.")

    def on_row_select(self, event):
        """Populate the form when the user selects a contact from the list."""
        selected = self.contacts_tree.selection()
        if not selected:
            return
        contact_id = selected[0]
        values = self.contacts_tree.item(contact_id, "values")
        self.name_var.set(values[0])
        self.email_var.set(values[1])
        self.phone_var.set(values[2])
        self.address_var.set(values[3])
        self.set_status(f"Selected contact ID {contact_id}.")

    def set_status(self, message):
        """Update the status label displayed at the bottom of the window."""
        self.status_var.set(message)

    def close(self):
        """Close the database connection before the application exits."""
        self.db_connection.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = ContactApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.close(), root.destroy()))
    root.mainloop()