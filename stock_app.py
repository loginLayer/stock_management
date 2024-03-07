import os
import re
import sqlite3
import tkinter as tk
import webbrowser
import tkinter.messagebox as messagebox
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk


class StockApp:
    def __init__(self, root):
        """
        Initialize the StockApp.

        Parameters:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("Stock Management App")
        self.root.geometry("700x490")

        # Dictionary to map Treeview labels to database identifiers
        self.id_mapping = {}

        # Variables for input fields
        self.product_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.code_var = tk.StringVar()

        # User interface
        self.create_widgets()

        # Database connection
        self.conn = sqlite3.connect('stock_database.db')
        self.create_table()

        # Show all products when the application starts
        self.update_table()

    def create_widgets(self):
        """
        Create the user interface widgets.
        """
        # Input fields
        tk.Label(self.root, text="Product:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.product_var).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.root, text="Description:").grid(row=0, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.description_var).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        tk.Label(self.root, text="Quantity:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.quantity_var).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        tk.Label(self.root, text="EAN/UPC Code:").grid(row=1, column=2, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.code_var).grid(row=1, column=3, padx=10, pady=5, sticky="w")

        # Buttons
        tk.Button(self.root, text="Add", command=self.add_product, width=10).grid(row=2, column=0, padx=10, pady=5)
        tk.Button(self.root, text="Update", command=self.update_product, width=10).grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Delete", command=self.delete_product, width=10).grid(row=2, column=2, padx=10, pady=5)
        tk.Button(self.root, text="Clear Form", command=self.clear_form, width=10).grid(row=2, column=3, padx=10, pady=5)

        # Table
        self.tree = ttk.Treeview(self.root, columns=("row_number", "product", "description", "quantity", "code", "date_added"), show="headings")
        self.tree.heading("row_number", text="#")
        self.tree.heading("product", text="Product")
        self.tree.heading("description", text="Description")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("code", text="EAN")
        self.tree.heading("date_added", text="Date Added")

        # Set column widths
        self.tree.column("row_number", width=50)  # Width of "Row Number" column
        self.tree.column("product", width=140)    # Width of "Product" column
        self.tree.column("description", width=210)  # Width of "Description" column
        self.tree.column("quantity", width=70)     # Width of "Quantity" column
        self.tree.column("code", width=100)        # Width of "Code" column
        self.tree.column("date_added", width=130)  # Width of "Date Added" column

        self.tree.grid(row=3, column=0, columnspan=4, padx=10, pady=5)

        # Search field
        self.search_var = tk.StringVar()
        tk.Label(self.root, text="Search products:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        tk.Entry(self.root, textvariable=self.search_var).grid(row=4, column=1, padx=10, pady=5, sticky="w")
        tk.Button(self.root, text="Search", command=self.search_product, width=10).grid(row=4, column=2, padx=10, pady=5, sticky="we")

        # Button to show all products
        tk.Button(self.root, text="Clear Search", command=self.show_all_products).grid(row=4, column=3, padx=10, pady=5, sticky="w")

        # Exit button
        exit_button = tk.Button(self.root, text="Exit", command=self.exit_app, width=20)
        exit_button.place(x=513, y=385)

        # Add a footer
        footer_frame = tk.Frame(self.root, bg="white", height=60, width=700)
        footer_frame.place(x=0, y=430)

        # Open the link when the user clicks on the footer image
        def open_github_link(event):
            webbrowser.open("https://github.com/loginLayer/stock_management")

        # Load and display the footer image
        footer_img_path = os.path.join(os.path.dirname(__file__), 'img', 'footer.png')
        footer_img = Image.open(footer_img_path)
        # Resize to fit the frame
        footer_img = footer_img.resize((700, 60), Image.BICUBIC)
        footer_img = ImageTk.PhotoImage(footer_img)
        # Use a Label with a link to open the URL
        footer_label = tk.Label(footer_frame, image=footer_img, bg="white", cursor="hand2")
        # Keep a reference to the image to prevent garbage collection
        footer_label.image = footer_img
        # Bind the click event to the function that opens the link
        footer_label.bind("<Button-1>", open_github_link)
        footer_label.pack()

    def create_table(self):
        """
        Create the database table if it does not exist.
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY,
                product TEXT NOT NULL,
                description TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                code TEXT NOT NULL,
                date_added TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_product(self):
        """
        Add a product to the database.

        Returns:
            None
        """
        product = self.product_var.get()
        description = self.description_var.get()
        quantity = self.quantity_var.get()
        code = self.code_var.get()
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.validate_code(code):
            if self.validate_quantity(quantity):
                if product and description and quantity and code:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        INSERT INTO stock (product, description, quantity, code, date_added)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (product, description, quantity, code, date_added))

                    self.conn.commit()
                    self.clear_form()
                    self.update_table()
            else:
                messagebox.showerror("Error", "Invalid Quantity. Please enter a valid number.")
        else:
            messagebox.showerror("Error", "Invalid EAN/UPC Code. Please enter a valid code.")

    def update_product(self):
        """
        Update a product in the database.

        Returns:
            None
        """
        selected_item = self.tree.selection()

        if not selected_item:
            return

        product = self.product_var.get()
        description = self.description_var.get()
        quantity = self.quantity_var.get()
        code = self.code_var.get()
        date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.validate_code(code):
            if self.validate_quantity(quantity):
                # Get the real database id using the mapping
                db_id = self.id_mapping.get(selected_item[0])

                if db_id:
                    cursor = self.conn.cursor()
                    cursor.execute('''
                        UPDATE stock
                        SET product=?, description=?, quantity=?, code=?, date_added=?
                        WHERE id=?
                    ''', (product, description, quantity, code, date_added, db_id))

                    self.conn.commit()
                    self.clear_form()
                    self.update_table()
                else:
                    print("Could not find database ID for the selected item.")
            else:
                messagebox.showerror("Error", "Invalid Quantity. Please enter a valid number.")
        else:
            messagebox.showerror("Error", "Invalid EAN/UPC Code. Please enter a valid code.")

    def validate_code(self, code):
        """
        Validate that the EAN/UPC code is a 12 or 13 digit integer.

        Parameters:
            code (str): The EAN/UPC code.

        Returns:
            bool: True if the code is valid, False otherwise.
        """
        return re.match(r'^\d{12,13}$', code) is not None

    def validate_quantity(self, quantity):
        """
        Validate that the quantity is a positive integer.

        Parameters:
            quantity (str): The quantity.

        Returns:
            bool: True if the quantity is valid, False otherwise.
        """
        return quantity.isdigit()

    def delete_product(self):
        """
        Delete a product from the database.

        Returns:
            None
        """
        selected_item = self.tree.selection()

        if not selected_item:
            return

        # Get the id directly from the selected row
        db_id = self.tree.item(selected_item[0], 'values')[0]

        if db_id:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM stock WHERE id=?', (db_id,))
            self.conn.commit()
            self.clear_form()
            self.update_table()

    def clear_form(self):
        """
        Clear all input fields.

        Returns:
            None
        """
        self.product_var.set('')
        self.description_var.set('')
        self.quantity_var.set('')
        self.code_var.set('')
        self.search_var.set('')

    def show_all_products(self):
        """
        Display all products in the table.

        Returns:
            None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, product, description, quantity, code, date_added FROM stock')
        self.display_data(cursor.fetchall())

    def search_product(self):
        """
        Search for products in the database based on the search term.

        Returns:
            None
        """
        search_term = self.search_var.get()
        cursor = self.conn.cursor()

        cursor.execute('''
            SELECT id, product, description, quantity, code, date_added
            FROM stock
            WHERE product LIKE ? OR
                description LIKE ? OR
                quantity LIKE ? OR
                code LIKE ? OR
                date_added LIKE ?
        ''', ('%' + search_term + '%',) * 5)

        self.display_data(cursor.fetchall())

    def update_table(self):
        """
        Update the Treeview with data from the database.

        Returns:
            None
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, product, description, quantity, code, date_added FROM stock')
        data = cursor.fetchall()

        # Clear mapping before updating
        self.id_mapping.clear()

        # Update Treeview and mapping
        self.display_data(data)

    def display_data(self, data):
        """
        Display data in the Treeview.

        Parameters:
            data (list): List of data rows.

        Returns:
            None
        """
        self.tree.delete(*self.tree.get_children())
        for row in data:
            # Convert to string to ensure the key is a string
            row_id_str = str(row[0])
            # Add to mapping
            self.id_mapping[row_id_str] = self.tree.insert('', 'end', iid=row[0], values=row)

    def exit_app(self):
        """
        Close the database connection and exit the application.

        Returns:
            None
        """
        self.conn.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
