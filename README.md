# 🏦 Secure Terminal Banking System

A robust, console-based banking management system implemented in **Python** leveraging **Object-Oriented Programming (OOP)** paradigms and a relational **SQLite3** database for permanent data persistence.

---

## 🌟 Key Features

- **Object-Oriented Architecture:** Designed using clean OOP principles including Abstraction, Encapsulation, Inheritance, and Polymorphism.
- **Relational Database (SQLite3):** Stores customer accounts and full transaction logs permanently across sessions.
- **Account Types & Inheritance:**
  - `SavingsAccount`: Earns 4% annual interest on the deposited balance.
  - `CurrentAccount`: Implements method overriding to support up to ₹10,000 overdraft limit.
- **Security & PIN Verification:** Private data attributes (`__balance`, `__pin`) protected against external modifications.
- **Mini-Statement / Ledger:** Tracks and displays formatted transaction logs (timestamp, type, amount, and running balance).

---

🛠️ Tech Stack

- **Language:** Python 3.x
- **Database:** SQLite3 (Embedded Relational DB)
- **Architecture:** Object-Oriented Programming (OOP)

---

## 🚀 How to Run

1. **Clone or Download the repository:**
   ```bash
   git clone [https://github.com/coderofsoumen/secure-banking-system-python.git](https://github.com/coderofsoumen/secure-banking-system-python.git)
   cd secure-banking-system-python




## 🖥️ Live Terminal Preview

```text
===================================
    SECURE SQLITE BANKING SYSTEM    
===================================
1. Open Account
2. Deposit Funds
3. Withdraw Funds
4. Check Mini-Statement
5. Apply Interest (Savings Only)
6. Exit
===================================
Enter choice (1-6): 1

--- Open New Account ---
Enter account holder's name: Soumen Shil
Set 4-digit PIN: 1234
Enter initial deposit (Min ₹500): 1000
Account Type (1 for Savings, 2 for Current): 1

Account Created Successfully!
Your Account Number is: 1001 (Please preserve this)
```
