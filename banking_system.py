from datetime import datetime
import sqlite3

# =====================================================================
# 1. DATABASE HANDLER CLASS (DATA PERSISTENCE)
# =====================================================================


class DatabaseManager:

  def __init__(self, db_name="bank_system.db"):
    self.db_name = db_name
    self.init_db()

  def get_connection(self):
    conn = sqlite3.connect(self.db_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

  def init_db(self):
    with self.get_connection() as conn:
      cursor = conn.cursor()

      # Accounts Table
      cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                acc_no INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pin INTEGER NOT NULL,
                balance REAL NOT NULL,
                acc_type TEXT NOT NULL,
                overdraft_limit REAL DEFAULT 0.0
            )
            """)

      cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                trans_id INTEGER PRIMARY KEY AUTOINCREMENT,
                acc_no INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                FOREIGN KEY (acc_no) REFERENCES accounts (acc_no) ON DELETE CASCADE
            )
            """)
      conn.commit()

  def insert_account(
      self,
      name: str,
      pin: int,
      balance: float,
      acc_type: str,
      overdraft_limit: float = 0.0,
  ) -> int:
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO accounts (name, pin, balance, acc_type, overdraft_limit)
                VALUES (?, ?, ?, ?, ?)
            """,
          (name, pin, balance, acc_type, overdraft_limit),
      )
      conn.commit()
      return cursor.lastrowid

  def update_balance(self, acc_no: int, new_balance: float):
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
          """
                UPDATE accounts SET balance = ? WHERE acc_no = ?
            """,
          (new_balance, acc_no),
      )
      conn.commit()

  def add_transaction(
      self, acc_no: int, t_type: str, amount: float, balance_after: float
  ):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
          """
                INSERT INTO transactions (acc_no, timestamp, type, amount, balance_after)
                VALUES (?, ?, ?, ?, ?)
            """,
          (acc_no, now, t_type, amount, balance_after),
      )
      conn.commit()

  def get_account_by_id(self, acc_no: int):
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT * FROM accounts WHERE acc_no = ?", (acc_no,))
      return cursor.fetchone()

  def get_transactions_by_id(self, acc_no: int, limit: int = 5):
    with self.get_connection() as conn:
      cursor = conn.cursor()
      cursor.execute(
          """
                SELECT timestamp, type, amount, balance_after 
                FROM transactions 
                WHERE acc_no = ? 
                ORDER BY trans_id DESC 
                LIMIT ?
            """,
          (acc_no, limit),
      )
      return cursor.fetchall()


# =====================================================================
# 2. OOP DOMAIN MODELS (ENCAPSULATION & INHERITANCE)
# =====================================================================


class Account:

  def __init__(
      self,
      acc_no: int,
      name: str,
      pin: int,
      balance: float,
      acc_type: str,
      db_manager: DatabaseManager,
  ):
    self.acc_no = acc_no
    self.name = name
    self._acc_type = acc_type
    self.__pin = pin  # Private Attribute (Encapsulation)
    self.__balance = balance  # Private Attribute (Encapsulation)
    self.db = db_manager

  def verify_pin(self, entered_pin: int) -> bool:
    return self.__pin == entered_pin

  def get_balance(self) -> float:
    return self.__balance

  def _set_balance(self, new_balance: float):
    self.__balance = new_balance
    self.db.update_balance(self.acc_no, new_balance)

  def deposit(self, amount: float):
    if amount <= 0:
      print("Deposit amount must be greater than zero.")
      return

    new_bal = self.get_balance() + amount
    self._set_balance(new_bal)
    self.db.add_transaction(self.acc_no, "Deposit", amount, new_bal)
    print(f"₹{amount:.2f} deposited successfully.")
    print(f"Updated Balance: ₹{self.get_balance():.2f}")

  def withdraw(self, amount: float) -> bool:
    if amount <= 0:
      print("Withdrawal amount must be greater than zero.")
      return False
    if amount > self.__balance:
      print(f"Insufficient balance! Available: ₹{self.__balance:.2f}")
      return False

    new_bal = self.get_balance() - amount
    self._set_balance(new_bal)
    self.db.add_transaction(self.acc_no, "Withdrawal", amount, new_bal)
    print(f"₹{amount:.2f} withdrawn successfully.")
    print(f"Remaining Balance: ₹{self.get_balance():.2f}")
    return True

  def display_statement(self):
    history = self.db.get_transactions_by_id(self.acc_no, limit=5)
    print(f"\n--- Mini Statement: {self.name} (A/C: {self.acc_no}) ---")
    print(f"Account Type   : {self._acc_type}")
    print(f"Current Balance: ₹{self.get_balance():.2f}")
    print("-" * 65)
    print(
        f"{'Date & Time':<20} | {'Type':<12} | {'Amount':<10} |"
        f" {'Net Balance':<10}"
    )
    print("-" * 65)
    if not history:
      print("No transactions recorded yet.")
    else:
      for row in history:
        timestamp, t_type, amount, balance_after = row
        print(
            f"{timestamp:<20} | {t_type:<12} | ₹{amount:<9.2f} |"
            f" ₹{balance_after:<9.2f}"
        )
    print("-" * 65)


class SavingsAccount(Account):

  def __init__(
      self,
      acc_no: int,
      name: str,
      pin: int,
      balance: float,
      db_manager: DatabaseManager,
  ):
    super().__init__(acc_no, name, pin, balance, "Savings", db_manager)
    self.interest_rate = 0.04  

  def apply_interest(self):
    interest = self.get_balance() * self.interest_rate
    new_bal = self.get_balance() + interest
    self._set_balance(new_bal)
    self.db.add_transaction(self.acc_no, "Interest", interest, new_bal)
    print(f"Annual interest of ₹{interest:.2f} credited to your account.")
    print(f"Updated Balance: ₹{self.get_balance():.2f}")


class CurrentAccount(Account):

  def __init__(
      self,
      acc_no: int,
      name: str,
      pin: int,
      balance: float,
      db_manager: DatabaseManager,
      overdraft_limit: float = 10000.0,
  ):
    super().__init__(acc_no, name, pin, balance, "Current", db_manager)
    self.overdraft_limit = overdraft_limit

  # Polymorphism (Method Overriding)
  def withdraw(self, amount: float) -> bool:
    if amount <= 0:
      print("Invalid amount.")
      return False

    available_funds = self.get_balance() + self.overdraft_limit
    if amount > available_funds:
      print(f"Limit exceeded! Total available limit: ₹{available_funds:.2f}")
      return False

    new_bal = self.get_balance() - amount
    self._set_balance(new_bal)
    self.db.add_transaction(self.acc_no, "Withdrawal (OD)", amount, new_bal)
    print(f"₹{amount:.2f} withdrawn successfully.")
    print(f"Net Balance: ₹{self.get_balance():.2f}")
    return True


# =====================================================================
# 3. CONTROLLER & USER INTERFACE
# =====================================================================


class BankController:

  def __init__(self):
    self.db = DatabaseManager()

  def open_account(self):
    print("\n--- Open New Account ---")
    name = input("Enter account holder's name: ").strip()
    if not name:
      print("Error: Name cannot be empty.")
      return

    try:
      pin = int(input("Set 4-digit PIN: "))
      deposit = float(input("Enter initial deposit (Min ₹500): "))
      acc_type_choice = input(
          "Account Type (1 for Savings, 2 for Current): "
      ).strip()
    except ValueError:
      print("Error: Please provide valid numerical inputs.")
      return

    if deposit < 500:
      print("Minimum initial deposit is ₹500.")
      return

    if acc_type_choice == "2":
      acc_type = "Current"
      od_limit = 10000.0
    else:
      acc_type = "Savings"
      od_limit = 0.0

   
    acc_no = self.db.insert_account(name, pin, deposit, acc_type, od_limit)
    self.db.add_transaction(acc_no, "Account Opened", deposit, deposit)

    print("\nAccount Created Successfully!")
    print(f"Your Account Number is: {acc_no} (Please preserve this)")

  def authenticate(self):
    try:
      acc_no = int(input("Enter Account Number: "))
      pin = int(input("Enter 4-digit PIN: "))
    except ValueError:
      print("Error: Account Number and PIN must be integers.")
      return None

    row = self.db.get_account_by_id(acc_no)
    if not row:
      print("Error: Account not found.")
      return None

    # row structure: (acc_no, name, pin, balance, acc_type, overdraft_limit)
    acc_num, name, stored_pin, balance, acc_type, od_limit = row

    if stored_pin != pin:
      print("Error: Incorrect PIN.")
      return None

    if acc_type == "Savings":
      return SavingsAccount(acc_num, name, stored_pin, balance, self.db)
    else:
      return CurrentAccount(
          acc_num, name, stored_pin, balance, self.db, od_limit
      )

  def run(self):
    while True:
      print("\n" + "=" * 35)
      print("    SECURE SQLITE BANKING SYSTEM    ")
      print("=" * 35)
      print("1. Open Account")
      print("2. Deposit Funds")
      print("3. Withdraw Funds")
      print("4. Check Mini-Statement")
      print("5. Apply Interest (Savings Only)")
      print("6. Exit")
      print("=" * 35)

      choice = input("Enter choice (1-6): ").strip()

      if choice == "1":
        self.open_account()

      elif choice == "2":
        account = self.authenticate()
        if account:
          try:
            amt = float(input("Enter deposit amount: ₹"))
            account.deposit(amt)
          except ValueError:
            print("Invalid input! Please enter a valid number.")

      elif choice == "3":
        account = self.authenticate()
        if account:
          try:
            amt = float(input("Enter withdrawal amount: ₹"))
            account.withdraw(amt)
          except ValueError:
            print("Invalid input! Please enter a valid number.")

      elif choice == "4":
        account = self.authenticate()
        if account:
          account.display_statement()

      elif choice == "5":
        account = self.authenticate()
        if account:
          if isinstance(account, SavingsAccount):
            account.apply_interest()
          else:
            print(
                "Interest calculation is only applicable for Savings Accounts."
            )

      elif choice == "6":
        print("\nDatabase session closed. Thank you for using our service!")
        break

      else:
        print("Invalid selection. Please choose between 1 and 6.")


if __name__ == "__main__":
  bank_app = BankController()
  bank_app.run()
