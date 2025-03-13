import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
import hashlib
import re
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Database Setup
conn = sqlite3.connect('bank.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                security_question TEXT,
                security_answer TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
                sr_no INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                customer_name TEXT,
                account_number TEXT,
                ifsc_code TEXT,
                mobile TEXT,
                address TEXT,
                transaction_no TEXT,
                transaction_type TEXT,
                transaction_mode TEXT,
                bank_name TEXT,
                amount REAL)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS balances (
                cash REAL DEFAULT 0)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS banks (
                bank_name TEXT PRIMARY KEY,
                balance REAL DEFAULT 0)""")

if not cursor.execute("SELECT 1 FROM balances").fetchone():
    cursor.execute("INSERT INTO balances (cash) VALUES (0)")
    conn.commit()

class BankingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Data Click Education - Banking System")
        self.root.geometry("1280x800")
        self.root.configure(bg='#f0f2f5')
        self.current_user = None
        self.selected_transaction = None
        self.blink_flag = True
        
        self.setup_styles()
        self.show_auth_screen()
        self.root.mainloop()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background='#f0f2f5')
        self.style.configure("Header.TLabel", 
                           font=('Arial', 24, 'bold'), 
                           foreground='#2d3436', 
                           background='#f0f2f5')
        self.style.configure("Shop.TLabel", 
                           font=('Arial', 18, 'bold'), 
                           foreground='#e74c3c',
                           background='#f0f2f5')
        self.style.configure("Balance.TLabel", 
                           font=('Arial', 14, 'bold'), 
                           foreground='#2d3436', 
                           background='#ffffff')
        
        self.style.configure('Cash.TLabelframe', 
                   background='#e8f5e9', 
                   bordercolor='#43a047',
                   relief='solid',
                   borderwidth=2)
        self.style.configure('Bank.TLabelframe', 
                   background='#e3f2fd', 
                   bordercolor='#1e88e5',
                   relief='solid',
                   borderwidth=2)
        self.style.configure('Total.TLabelframe', 
                   background='#f3e5f5', 
                   bordercolor='#8e24aa',
                   relief='solid',
                   borderwidth=2)
        self.style.configure('Deposit.TLabelframe', 
                   background='#e0f2f1', 
                   bordercolor='#009688',
                   relief='solid',
                   borderwidth=2)
        self.style.configure('Withdrawal.TLabelframe', 
                   background='#ffebee', 
                   bordercolor='#e53935',
                   relief='solid',
                   borderwidth=2)
        self.style.configure('Closing.TLabelframe', 
                   background='#eceff1', 
                   bordercolor='#607d8b',
                   relief='solid',
                   borderwidth=2)
        self.style.configure("TButton", 
                           font=('Arial', 12), 
                           padding=8,
                           foreground='white', 
                           background='#0984e3')
        self.style.map("TButton", 
                      background=[('active', '#74b9ff')])
        self.style.configure("Red.TButton", background='#d63031')
        self.style.configure("Green.TButton", background='#2ecc71')
        self.style.configure("Orange.TButton", background='#e67e22')
        self.style.configure("Purple.TButton", background='#9b59b6')
        self.style.map("Green.TButton", background=[('active', '#27ae60')])
        self.style.map("Orange.TButton", background=[('active', '#d35400')])
        self.style.map("Purple.TButton", background=[('active', '#8e44ad')])
        self.style.configure("Treeview", 
                           font=('Arial', 11), 
                           rowheight=25,
                           background='#ffffff', 
                           fieldbackground='#ffffff')
        self.style.configure("Treeview.Heading", 
                           font=('Arial', 12, 'bold'),
                           background='#0984e3', 
                           foreground='white')

    def toggle_blink(self):
        if self.blink_flag:
            self.shop_label.config(foreground='#e74c3c')
        else:
            self.shop_label.config(foreground='#f0f2f5')
        self.blink_flag = not self.blink_flag
        self.root.after(500, self.toggle_blink)

    # Authentication System 
    def show_auth_screen(self):
        if hasattr(self, 'reg_frame'):
            self.reg_frame.destroy()
        if hasattr(self, 'forgot_frame'):
            self.forgot_frame.destroy()
        
        self.auth_frame = ttk.Frame(self.root)
        self.auth_frame.pack(pady=100, fill=tk.BOTH, expand=True)
        
        login_card = ttk.Frame(self.auth_frame, style='TLabelframe')
        login_card.pack(padx=200, pady=50, ipadx=20, ipady=20)
        
        ttk.Label(login_card, text="Banking System", style="Header.TLabel").pack(pady=20)
        
        form_frame = ttk.Frame(login_card)
        form_frame.pack(padx=50, pady=20)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, pady=10)
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, pady=10)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, pady=10)
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=10)
        
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=2, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Login", command=self.login).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Register", command=self.show_registration).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Forgot Password", command=self.show_forgot_password,
                  style="Red.TButton").pack(side=tk.LEFT, padx=10)

    def show_registration(self):
        self.auth_frame.destroy()
        self.reg_frame = ttk.Frame(self.root)
        self.reg_frame.pack(pady=100, fill=tk.BOTH, expand=True)

        reg_card = ttk.Frame(self.reg_frame, style='TLabelframe')
        reg_card.pack(padx=200, pady=50, ipadx=20, ipady=20)

        ttk.Label(reg_card, text="New User Registration", style="Header.TLabel").pack(pady=20)

        form_frame = ttk.Frame(reg_card)
        form_frame.pack(padx=50, pady=20)

        fields = [
            ("Username:", "reg_username"),
            ("Password:", "reg_password"),
            ("Security Question:", "security_question"),
            ("Security Answer:", "security_answer")
        ]

        for i, (text, var) in enumerate(fields):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, pady=5, sticky='e')
            entry = ttk.Entry(form_frame, show="*" if "password" in var else "")
            entry.grid(row=i, column=1, pady=5, padx=5)
            setattr(self, var, entry)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Register", command=self.register_user).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Back", command=self.back_to_login, style="Red.TButton").pack(side=tk.LEFT, padx=10)

    def show_forgot_password(self):
        self.auth_frame.destroy()
        self.forgot_frame = ttk.Frame(self.root)
        self.forgot_frame.pack(pady=100, fill=tk.BOTH, expand=True)

        forgot_card = ttk.Frame(self.forgot_frame, style='TLabelframe')
        forgot_card.pack(padx=200, pady=50, ipadx=20, ipady=20)

        ttk.Label(forgot_card, text="Password Recovery", style="Header.TLabel").pack(pady=20)

        form_frame = ttk.Frame(forgot_card)
        form_frame.pack(padx=50, pady=20)

        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, pady=5, sticky='e')
        self.recovery_user = ttk.Entry(form_frame)
        self.recovery_user.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Security Question:").grid(row=1, column=0, pady=5, sticky='e')
        self.security_ques = ttk.Label(form_frame, text="")
        self.security_ques.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Answer:").grid(row=2, column=0, pady=5, sticky='e')
        self.security_ans = ttk.Entry(form_frame)
        self.security_ans.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="New Password:").grid(row=3, column=0, pady=5, sticky='e')
        self.new_password = ttk.Entry(form_frame, show="*")
        self.new_password.grid(row=3, column=1, pady=5, padx=5)

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Get Question", command=self.fetch_security_question).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset Password", command=self.reset_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Back", command=self.back_to_login, style="Red.TButton").pack(side=tk.LEFT, padx=5)

    def register_user(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        security_question = self.security_question.get()
        security_answer = self.security_answer.get()

        if not all([username, password, security_question, security_answer]):
            messagebox.showerror("Error", "All fields are required!")
            return

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        hashed_answer = hashlib.sha256(security_answer.encode()).hexdigest()

        try:
            cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                         (username, hashed_pw, security_question, hashed_answer))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            self.back_to_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return

        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
        user = cursor.fetchone()

        if user:
            self.current_user = username
            self.auth_frame.destroy()
            self.show_main_app()
            self.update_balances()
            self.load_transactions()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def fetch_security_question(self):
        username = self.recovery_user.get()
        cursor.execute("SELECT security_question FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        
        if result:
            self.security_ques.config(text=result[0])
        else:
            messagebox.showerror("Error", "Username not found")

    def reset_password(self):
        username = self.recovery_user.get()
        answer = self.security_ans.get()
        new_pw = self.new_password.get()
        
        if not all([username, answer, new_pw]):
            messagebox.showerror("Error", "All fields are required!")
            return
            
        hashed_answer = hashlib.sha256(answer.encode()).hexdigest()
        cursor.execute("SELECT 1 FROM users WHERE username=? AND security_answer=?", (username, hashed_answer))
        
        if cursor.fetchone():
            new_hashed_pw = hashlib.sha256(new_pw.encode()).hexdigest()
            cursor.execute("UPDATE users SET password=? WHERE username=?", (new_hashed_pw, username))
            conn.commit()
            messagebox.showinfo("Success", "Password reset successful!")
            self.back_to_login()
        else:
            messagebox.showerror("Error", "Invalid security answer")

    def back_to_login(self):
        if hasattr(self, 'reg_frame'):
            self.reg_frame.destroy()
        if hasattr(self, 'forgot_frame'):
            self.forgot_frame.destroy()
        self.show_auth_screen()

    # Main Banking Interface
    def show_main_app(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        # Blinking Shop Name
        self.shop_label = ttk.Label(header_frame, 
                                  text="Data Click Education", 
                                  style="Shop.TLabel")
        self.shop_label.pack(side=tk.LEFT, padx=20)
        self.toggle_blink()
        
        ttk.Button(header_frame, 
                 text="Logout", 
                 command=self.logout, 
                 style="Red.TButton").pack(side=tk.RIGHT)
        
        # Search Bar
        self.search_entry = ttk.Entry(header_frame)
        self.search_entry.pack(side=tk.RIGHT, padx=10)
        self.search_entry.insert(0, "Type here to search")
        
        # Main Content
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar_frame = ttk.Frame(content_frame, width=250)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Balance Management
        balance_frame = ttk.LabelFrame(sidebar_frame, text="Balance Management")
        balance_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(balance_frame, text="Cash:").pack(pady=5, anchor='w')
        self.cash_entry = ttk.Entry(balance_frame)
        self.cash_entry.pack(pady=5, fill=tk.X)
        
        # Bank Management
        bank_management_frame = ttk.LabelFrame(balance_frame, text="Bank Management")
        bank_management_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(bank_management_frame, text="Bank Name:").pack(anchor='w')
        self.bank_name_entry = ttk.Entry(bank_management_frame)
        self.bank_name_entry.pack(fill=tk.X)
        
        ttk.Label(bank_management_frame, text="Balance:").pack(anchor='w')
        self.bank_balance_entry = ttk.Entry(bank_management_frame)
        self.bank_balance_entry.pack(fill=tk.X)
        
        btn_frame = ttk.Frame(bank_management_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Add/Update", command=self.add_update_bank).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_bank, style="Red.TButton").pack(side=tk.LEFT, padx=2)
        
        btn_frame = ttk.Frame(balance_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Set Cash", command=self.set_balances).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reset Cash", command=self.reset_balances, style="Red.TButton").pack(side=tk.LEFT, padx=5)
        
        # Transactions
        txn_frame = ttk.LabelFrame(sidebar_frame, text="Transactions")
        txn_frame.pack(pady=10, fill=tk.X)
        ttk.Button(txn_frame, text="New Transaction", command=self.show_transaction_window).pack(pady=10)
        
        # Reports
        report_frame = ttk.LabelFrame(sidebar_frame, text="Reports")
        report_frame.pack(pady=10, fill=tk.X)
        ttk.Button(report_frame, text="Generate Report", command=self.show_report_dialog).pack(pady=10)
        
        # Main Content Area
        main_content = ttk.Frame(content_frame)
        main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Balance Display
        balance_display_frame = ttk.Frame(main_content)
        balance_display_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Cash Balance
        cash_frame = ttk.LabelFrame(balance_display_frame, text="💵 Cash", style='Cash.TLabelframe')
        cash_frame.pack(side=tk.LEFT, padx=5, pady=5)
        self.cash_balance = ttk.Label(cash_frame, text="₹0.00", font=('Arial', 12, 'bold'))
        self.cash_balance.pack(padx=10, pady=5)
        
        # Bank Balances Container
        self.banks_container = ttk.Frame(balance_display_frame)
        self.banks_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Other Balances
        other_balances_frame = ttk.Frame(balance_display_frame)
        other_balances_frame.pack(side=tk.LEFT, padx=5)
        
        balance_items = [
            ("💰 Total", "total_balance", 'Total.TLabelframe'),
            ("⬆️ Deposit", "total_deposit", 'Deposit.TLabelframe'),
            ("⬇️ Withdrawal", "total_withdrawal", 'Withdrawal.TLabelframe'),
            ("🏦 Closing", "closing_balance", 'Closing.TLabelframe')
        ]
        
        for label, name, style_name in balance_items:
            frame = ttk.LabelFrame(other_balances_frame, text=label, style=style_name)
            frame.pack(side=tk.LEFT, padx=5, pady=5)
            lbl = ttk.Label(frame, text="₹0.00", font=('Arial', 12, 'bold'))
            lbl.pack(padx=10, pady=5)
            setattr(self, name, lbl)
        
        # Transaction History
        history_frame = ttk.LabelFrame(main_content, text="Transaction History")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Date Filter Section
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(filter_frame, text="From:").pack(side=tk.LEFT)
        self.start_filter_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.start_filter_date.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="To:").pack(side=tk.LEFT)
        self.end_filter_date = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.end_filter_date.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_date_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Clear Filter", command=self.clear_date_filter, style="Red.TButton").pack(side=tk.LEFT)

        # Action Buttons
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=5)

        actions = [
            ("Edit", self.edit_transaction, "TButton"),
            ("Delete", self.delete_transaction, "Red.TButton"),
            ("Print Receipt", self.print_receipt, "Green.TButton"),
            ("Details", self.show_transaction_details, "Purple.TButton"),
            ("Refresh", self.load_transactions, "Orange.TButton")
        ]

        for text, cmd, style in actions:
            ttk.Button(button_frame, text=text, command=cmd, style=style, width=12).pack(side=tk.LEFT, padx=3)

        # Transaction Treeview
        columns = [
            ("Sr.No", 50), 
            ("Date", 150), 
            ("Customer", 200), 
            ("Account No", 120), 
            ("IFSC Code", 100), 
            ("Mobile", 100), 
            ("Type", 80), 
            ("Mode", 80), 
            ("Bank", 100),
            ("Amount", 100)
        ]
        
        self.history_tree = ttk.Treeview(
            history_frame, 
            columns=[c[0] for c in columns], 
            show="headings",
            height=25,
            selectmode='browse'
        )
        
        for col in columns:
            self.history_tree.heading(col[0], text=col[0])
            self.history_tree.column(col[0], width=col[1], anchor=tk.CENTER)
            
        vsb = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        hsb = ttk.Scrollbar(history_frame, orient="horizontal", command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

    def apply_date_filter(self):
        start_date = self.start_filter_date.get_date()
        end_date = self.end_filter_date.get_date()
        self.load_transactions(start_date, end_date)

    def clear_date_filter(self):
        self.start_filter_date.set_date(datetime.now())
        self.end_filter_date.set_date(datetime.now())
        self.load_transactions()

    def show_daily_summary(self):
        cursor.execute('''SELECT 
                        date(date) as trans_date,
                        SUM(CASE WHEN transaction_type='Deposit' THEN amount ELSE 0 END) as total_deposit,
                        SUM(CASE WHEN transaction_type='Withdrawal' THEN amount ELSE 0 END) as total_withdrawal
                        FROM transactions
                        GROUP BY trans_date
                        ORDER BY trans_date DESC''')
        data = cursor.fetchall()
        
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Daily Transaction Summary")
        summary_window.geometry("600x400")
        
        tree = ttk.Treeview(summary_window, columns=('Date', 'Deposits', 'Withdrawals'), show='headings')
        tree.heading('Date', text='Date')
        tree.heading('Deposits', text='Total Deposits')
        tree.heading('Withdrawals', text='Total Withdrawals')
        
        tree.column('Date', width=150, anchor=tk.CENTER)
        tree.column('Deposits', width=200, anchor=tk.CENTER)
        tree.column('Withdrawals', width=200, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(summary_window, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(summary_window, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        for row in data:
            tree.insert("", tk.END, values=(
                row[0],
                f"₹{row[1]:,.2f}",
                f"₹{row[2]:,.2f}"
            ))
            
        tree.pack(fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

    def get_selected_transaction(self):
        selected_item = self.history_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a transaction first!")
            return None
        return self.history_tree.item(selected_item[0])['values'][0]

    def edit_transaction(self):
        self.selected_transaction = self.get_selected_transaction()
        if not self.selected_transaction:
            return
        
        cursor.execute("SELECT * FROM transactions WHERE sr_no=?", (self.selected_transaction,))
        transaction = cursor.fetchone()
        
        self.txn_window = tk.Toplevel(self.root)
        self.txn_window.title("Edit Transaction")
        self.txn_window.geometry("400x500")
        
        form_frame = ttk.Frame(self.txn_window)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        fields = [
            ("Customer Name*:", "txn_customer", transaction[2]),
            ("Account No*:", "txn_account", transaction[3]),
            ("IFSC Code*:", "txn_ifsc", transaction[4]),
            ("Mobile*:", "txn_mobile", transaction[5]),
            ("Address:", "txn_address", transaction[6]),
            ("Transaction No*:", "txn_number", transaction[7]),
            ("Amount*:", "txn_amount", transaction[11]),
            ("Type*:", "txn_type", transaction[8]),
            ("Mode*:", "txn_mode", transaction[9]),
            ("Bank:", "txn_bank", transaction[10])
        ]
        
        self.entries = {}
        for i, (label, var, value) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, pady=5, sticky='e')
            if "Type" in label or "Mode" in label:
                values = ["Deposit", "Withdrawal"] if "Type" in label else ["Cash", "Bank"]
                entry = ttk.Combobox(form_frame, values=values, state="readonly")
                entry.current(values.index(value))
            elif "Bank" in label:
                entry = ttk.Combobox(form_frame, state="readonly")
                cursor.execute("SELECT bank_name FROM banks")
                banks = [row[0] for row in cursor.fetchall()]
                entry['values'] = banks
                if value in banks:
                    entry.current(banks.index(value))
                else:
                    entry.current(0)
            else:
                entry = ttk.Entry(form_frame)
                entry.insert(0, value)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky='ew')
            self.entries[var] = entry
        
        ttk.Button(form_frame, text="Update", command=self.update_transaction).grid(row=10, columnspan=2, pady=15)

    def update_transaction(self):
        try:
            cursor.execute('''UPDATE transactions SET
                            date=?, 
                            customer_name=?, 
                            account_number=?, 
                            ifsc_code=?, 
                            mobile=?, 
                            address=?, 
                            transaction_no=?, 
                            transaction_type=?, 
                            transaction_mode=?, 
                            bank_name=?,
                            amount=?
                            WHERE sr_no=?''',
                            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             self.entries['txn_customer'].get(),
                             self.entries['txn_account'].get(),
                             self.entries['txn_ifsc'].get(),
                             self.entries['txn_mobile'].get(),
                             self.entries['txn_address'].get(),
                             self.entries['txn_number'].get(),
                             self.entries['txn_type'].get(),
                             self.entries['txn_mode'].get(),
                             self.entries['txn_bank'].get() if self.entries['txn_mode'].get() == "Bank" else None,
                             float(self.entries['txn_amount'].get()),
                             self.selected_transaction))
            conn.commit()
            self.update_balances()
            self.load_transactions()
            self.txn_window.destroy()
            messagebox.showinfo("Success", "Transaction updated!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_transaction(self):
        self.selected_transaction = self.get_selected_transaction()
        if not self.selected_transaction:
            return
        
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?")
        if confirm:
            cursor.execute("DELETE FROM transactions WHERE sr_no=?", (self.selected_transaction,))
            conn.commit()
            self.update_balances()
            self.load_transactions()
            messagebox.showinfo("Success", "Transaction deleted!")

    def print_receipt(self):
        self.selected_transaction = self.get_selected_transaction()
        if not self.selected_transaction:
            return
        
        cursor.execute("SELECT * FROM transactions WHERE sr_no=?", (self.selected_transaction,))
        transaction = cursor.fetchone()
        
        filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                               filetypes=[("PDF Files", "*.pdf")])
        if filename:
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='ShopStyle', 
                                    fontSize=18,
                                    textColor=colors.HexColor('#e74c3c'),
                                    alignment=1,
                                    spaceAfter=20))
            
            elements.append(Paragraph("Data Click Education", styles['ShopStyle']))
            elements.append(Paragraph("Bank Receipt", styles['Title']))
            elements.append(Spacer(1, 12))
            
            data = [
                ["Transaction No:", transaction[7]],
                ["Date:", transaction[1]],
                ["Customer Name:", transaction[2]],
                ["Account No:", transaction[3]],
                ["IFSC Code:", transaction[4]],
                ["Amount:", f"₹{transaction[11]:,.2f}"],
                ["Transaction Type:", transaction[8]],
                ["Mode:", transaction[9]],
                ["Bank:", transaction[10] if transaction[10] else "N/A"]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F81BD')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elements.append(table)
            
            doc.build(elements)
            messagebox.showinfo("Success", "Receipt saved successfully!")

    def show_transaction_details(self):
        self.selected_transaction = self.get_selected_transaction()
        if not self.selected_transaction:
            return
        
        cursor.execute("SELECT * FROM transactions WHERE sr_no=?", (self.selected_transaction,))
        transaction = cursor.fetchone()
        
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Transaction Details")
        detail_window.geometry("400x400")
        
        info_frame = ttk.Frame(detail_window)
        info_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        fields = [
            ("Transaction No:", transaction[7]),
            ("Date:", transaction[1]),
            ("Customer Name:", transaction[2]),
            ("Account No:", transaction[3]),
            ("IFSC Code:", transaction[4]),
            ("Mobile:", transaction[5]),
            ("Address:", transaction[6]),
            ("Type:", transaction[8]),
            ("Mode:", transaction[9]),
            ("Bank:", transaction[10] if transaction[10] else "N/A"),
            ("Amount:", f"₹{transaction[11]:,.2f}")
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(info_frame, text=label, font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky='w', pady=2)
            ttk.Label(info_frame, text=value).grid(row=i, column=1, sticky='w', pady=2)

    # Transaction Management
    def show_transaction_window(self):
        self.txn_window = tk.Toplevel(self.root)
        self.txn_window.title("New Transaction")
        self.txn_window.geometry("400x500")
        
        form_frame = ttk.Frame(self.txn_window)
        form_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        fields = [
            ("Customer Name*:", "txn_customer"),
            ("Account No*:", "txn_account"),
            ("IFSC Code*:", "txn_ifsc"),
            ("Mobile*:", "txn_mobile"),
            ("Address:", "txn_address"),
            ("Transaction No*:", "txn_number"),
            ("Amount*:", "txn_amount"),
            ("Type*:", "txn_type"),
            ("Mode*:", "txn_mode")
        ]
        
        for i, (label, var) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, pady=5, sticky='e')
            if "Type" in label or "Mode" in label:
                values = ["Deposit", "Withdrawal"] if "Type" in label else ["Cash", "Bank"]
                entry = ttk.Combobox(form_frame, values=values, state="readonly")
                entry.current(0)
            else:
                entry = ttk.Entry(form_frame)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky='ew')
            setattr(self, var, entry)
        
        # Bank selection
        self.bank_label = ttk.Label(form_frame, text="Bank*:")
        self.bank_combobox = ttk.Combobox(form_frame, state="readonly")
        self.bank_label.grid(row=9, column=0, pady=5, sticky='e')
        self.bank_combobox.grid(row=9, column=1, pady=5, padx=5, sticky='ew')
        self.bank_label.grid_remove()
        self.bank_combobox.grid_remove()
        
        self.txn_mode.bind("<<ComboboxSelected>>", self.on_mode_selected)
        
        ttk.Button(form_frame, text="Submit", command=self.add_transaction).grid(row=10, columnspan=2, pady=15)

    def on_mode_selected(self, event=None):
        if self.txn_mode.get() == "Bank":
            cursor.execute("SELECT bank_name FROM banks")
            banks = [row[0] for row in cursor.fetchall()]
            if not banks:
                messagebox.showerror("Error", "No banks available. Please add a bank first.")
                self.txn_mode.current(0)
                return
            self.bank_combobox['values'] = banks
            self.bank_combobox.current(0)
            self.bank_label.grid()
            self.bank_combobox.grid()
        else:
            self.bank_label.grid_remove()
            self.bank_combobox.grid_remove()

    def add_transaction(self):
        try:
            if not self.validate_ifsc(self.txn_ifsc.get()):
                raise ValueError("Invalid IFSC Code")
                
            if not self.validate_mobile(self.txn_mobile.get()):
                raise ValueError("Invalid Mobile Number")
                
            amount = float(self.txn_amount.get())
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            txn_type = self.txn_type.get()
            txn_mode = self.txn_mode.get()
            bank_name = self.bank_combobox.get() if txn_mode == "Bank" else None
            
            # Insert transaction
            cursor.execute('''INSERT INTO transactions 
                            (date, customer_name, account_number, ifsc_code, mobile, address,
                             transaction_no, transaction_type, transaction_mode, bank_name, amount)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             self.txn_customer.get(),
                             self.txn_account.get(),
                             self.txn_ifsc.get(),
                             self.txn_mobile.get(),
                             self.txn_address.get(),
                             self.txn_number.get(),
                             txn_type,
                             txn_mode,
                             bank_name,
                             amount))
            
            # Update balances
            if txn_type == "Deposit":
                if txn_mode == "Cash":
                    cursor.execute("UPDATE balances SET cash = cash + ?", (amount,))
                elif txn_mode == "Bank":
                    cursor.execute("UPDATE banks SET balance = balance + ? WHERE bank_name=?", (amount, bank_name))
            elif txn_type == "Withdrawal":
                if txn_mode == "Cash":
                    cursor.execute("UPDATE balances SET cash = cash - ?", (amount,))
                elif txn_mode == "Bank":
                    cursor.execute("UPDATE banks SET balance = balance - ? WHERE bank_name=?", (amount, bank_name))
            
            conn.commit()
            self.update_balances()
            self.load_transactions()
            self.txn_window.destroy()
            messagebox.showinfo("Success", "Transaction added!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Bank Management
    def add_update_bank(self):
        bank_name = self.bank_name_entry.get()
        balance = self.bank_balance_entry.get()
        if not bank_name or not balance:
            messagebox.showerror("Error", "Bank name and balance are required")
            return
        try:
            balance = float(balance)
            cursor.execute("INSERT OR REPLACE INTO banks (bank_name, balance) VALUES (?, ?)",
                         (bank_name, balance))
            conn.commit()
            self.update_balances()
            messagebox.showinfo("Success", "Bank balance updated")
        except ValueError:
            messagebox.showerror("Error", "Invalid balance")

    def delete_bank(self):
        bank_name = self.bank_name_entry.get()
        if not bank_name:
            messagebox.showerror("Error", "Enter bank name to delete")
            return
        cursor.execute("DELETE FROM banks WHERE bank_name=?", (bank_name,))
        conn.commit()
        if cursor.rowcount == 0:
            messagebox.showerror("Error", "Bank not found")
        else:
            messagebox.showinfo("Success", "Bank deleted")
        self.update_balances()

    # Reporting System
    def show_report_dialog(self):
        self.report_window = tk.Toplevel(self.root)
        self.report_window.title("Reports & Utilities")
        self.report_window.geometry("500x450")
        
        main_frame = ttk.Frame(self.report_window)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        ttk.Button(main_frame, text="Show Daily Summary", 
                 command=self.show_daily_summary).pack(pady=5)

        date_frame = ttk.LabelFrame(main_frame, text="Select Date Range")
        date_frame.pack(fill=tk.X, pady=5)

        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(date_frame, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5)

        ttk.Label(date_frame, text="End Date:").grid(row=1, column=0, padx=5)
        self.end_date = DateEntry(date_frame, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=1, column=1, padx=5)

        ttk.Label(date_frame, text="Report Type:").grid(row=2, column=0, padx=5)
        self.report_type = ttk.Combobox(date_frame, 
                                      values=["Summary", "Detailed", "Graphical"])
        self.report_type.current(0)
        self.report_type.grid(row=2, column=1, padx=5)

        export_frame = ttk.LabelFrame(main_frame, text="Data Management")
        export_frame.pack(fill=tk.X, pady=5)

        buttons = [
            ("Export PDF", self.export_pdf),
            ("Export Excel", self.export_excel),
            ("Export CSV", self.export_csv),
            ("Import CSV", self.import_csv)
        ]

        for text, cmd in buttons:
            ttk.Button(export_frame, text=text, command=cmd).pack(side=tk.LEFT, padx=5)

        ttk.Button(main_frame, text="Generate Report", 
                  command=self.generate_report).pack(pady=5)
        ttk.Button(main_frame, text="Close", 
                  command=self.report_window.destroy, style="Red.TButton").pack(pady=10)

    def generate_report(self):
        try:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()
            report_type = self.report_type.get()

            query = f"""SELECT * FROM transactions 
                      WHERE date BETWEEN '{start_date}' AND '{end_date}'"""
            
            cursor.execute(query)
            data = cursor.fetchall()
            
            if report_type == "Summary":
                summary = pd.read_sql_query(query, conn)
                summary = summary.groupby(['transaction_type', 'transaction_mode'])['amount'].sum()
                messagebox.showinfo("Summary Report", str(summary))
            
            elif report_type == "Detailed":
                self.show_detailed_report(data)
            
            elif report_type == "Graphical":
                self.generate_graphical_report(data)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_detailed_report(self, data):
        report_win = tk.Toplevel(self.root)
        report_win.title("Detailed Report")
        
        text = tk.Text(report_win, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True)
        
        columns = [description[0] for description in cursor.description]
        text.insert(tk.END, "\t".join(columns) + "\n")
        for row in data:
            text.insert(tk.END, "\t".join(map(str, row)) + "\n")

    def generate_graphical_report(self, data):
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        fig = plt.Figure(figsize=(6,4))
        ax = fig.add_subplot(111)
        df.groupby('transaction_type')['amount'].sum().plot(kind='bar', ax=ax)
        ax.set_title('Transaction Summary')
        
        chart_win = tk.Toplevel(self.root)
        canvas = FigureCanvasTkAgg(fig, chart_win)
        canvas.get_tk_widget().pack()

    def export_pdf(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")]
            )
            if filename:
                cursor.execute("SELECT * FROM transactions")
                data = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = []
                
                styles = getSampleStyleSheet()
                elements.append(Paragraph("Data Click Education", styles['Title']))
                elements.append(Spacer(1, 12))
                
                table_data = [columns] + list(data)
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.blue),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0,0), (-1,0), 12),
                    ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                    ('GRID', (0,0), (-1,-1), 1, colors.black)
                ]))
                elements.append(table)
                doc.build(elements)
                messagebox.showinfo("Success", "PDF exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_excel(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")]
            )
            if filename:
                cursor.execute("SELECT * FROM transactions")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=[
                    'sr_no', 'date', 'customer_name', 'account_number',
                    'ifsc_code', 'mobile', 'address', 'transaction_no',
                    'transaction_type', 'transaction_mode', 'bank_name', 'amount'
                ])
                df.to_excel(filename, index=False)
                messagebox.showinfo("Success", "Excel file exported!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")]
            )
            if filename:
                cursor.execute("SELECT * FROM transactions")
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=[
                    'sr_no', 'date', 'customer_name', 'account_number',
                    'ifsc_code', 'mobile', 'address', 'transaction_no',
                    'transaction_type', 'transaction_mode', 'bank_name', 'amount'
                ])
                df.to_csv(filename, index=False)
                messagebox.showinfo("Success", "CSV file exported!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def import_csv(self):
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV Files", "*.csv")]
            )
            if filename:
                df = pd.read_csv(filename)
                required_columns = [
                    'customer_name', 'account_number', 'ifsc_code', 'mobile',
                    'transaction_no', 'transaction_type', 'transaction_mode', 'amount'
                ]
                
                if not all(col in df.columns for col in required_columns):
                    raise ValueError("Invalid CSV format")
                
                for _, row in df.iterrows():
                    cursor.execute('''INSERT INTO transactions 
                        (date, customer_name, account_number, ifsc_code, mobile, address,
                         transaction_no, transaction_type, transaction_mode, amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         row['customer_name'], row['account_number'], row['ifsc_code'],
                         str(row['mobile']), row.get('address', ''),
                         row['transaction_no'], row['transaction_type'],
                         row['transaction_mode'], row['amount']))
                conn.commit()
                self.load_transactions()
                messagebox.showinfo("Success", f"{len(df)} transactions imported!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Utility Functions
    def validate_ifsc(self, code):
        return re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", code)

    def validate_mobile(self, number):
        return re.match(r"^[6-9]\d{9}$", number)

    def update_balances(self):
        # Update cash balance
        cursor.execute("SELECT cash FROM balances")
        cash = cursor.fetchone()[0]
        self.cash_balance.config(text=f"₹{cash:,.2f}")
        
        # Clear existing bank displays
        for widget in self.banks_container.winfo_children():
            widget.destroy()
        
        # Update bank balances
        cursor.execute("SELECT bank_name, balance FROM banks")
        banks = cursor.fetchall()
        for bank_name, balance in banks:
            frame = ttk.LabelFrame(self.banks_container, text=bank_name, style='Bank.TLabelframe')
            frame.pack(side=tk.LEFT, padx=5, pady=5)
            lbl = ttk.Label(frame, text=f"₹{balance:,.2f}", font=('Arial', 12, 'bold'))
            lbl.pack(padx=10, pady=5)
        
        # Calculate total balance
        cursor.execute("SELECT SUM(balance) FROM banks")
        total_bank = cursor.fetchone()[0] or 0
        total = cash + total_bank
        
        # Update other balances
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type='Deposit'")
        deposits = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE transaction_type='Withdrawal'")
        withdrawals = cursor.fetchone()[0] or 0
        
        self.total_balance.config(text=f"₹{total:,.2f}")
        self.total_deposit.config(text=f"₹{deposits:,.2f}")
        self.total_withdrawal.config(text=f"₹{withdrawals:,.2f}")
        self.closing_balance.config(text=f"₹{total:,.2f}")

    def load_transactions(self, start_date=None, end_date=None):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        query = '''SELECT 
                sr_no,
                date, 
                customer_name, 
                account_number,
                ifsc_code,
                mobile,
                transaction_type, 
                transaction_mode, 
                bank_name,
                amount 
                FROM transactions'''
        
        params = ()
        if start_date and end_date:
            query += " WHERE date(date) BETWEEN ? AND ?"
            params = (start_date, end_date)
        
        query += " ORDER BY date DESC"
        
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            formatted_row = (
                row[0],  # Sr.No
                row[1],  # Date
                row[2],  # Customer
                row[3],  # Account
                row[4],  # IFSC
                row[5],  # Mobile
                row[6],  # Type
                row[7],  # Mode
                row[8] if row[8] else "",  # Bank
                f"₹{row[9]:,.2f}"  # Amount
            )
            self.history_tree.insert("", tk.END, values=formatted_row)

    def set_balances(self):
        try:
            cash = float(self.cash_entry.get())
            cursor.execute("UPDATE balances SET cash=?", (cash,))
            conn.commit()
            self.update_balances()
        except ValueError:
            messagebox.showerror("Error", "Invalid cash amount")

    def reset_balances(self):
        self.cash_entry.delete(0, tk.END)
        self.cash_entry.insert(0, "0")
        self.set_balances()

    def logout(self):
        self.main_frame.destroy()
        self.current_user = None
        self.show_auth_screen()

if __name__ == "__main__":
    BankingApp()