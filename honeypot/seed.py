import psycopg2
from faker import Faker
import random
import time

fake = Faker("en_IN")

def wait_for_db():
    import os
    while True:
        try:
            conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=os.environ.get("DB_PORT", 5432),
                dbname=os.environ.get("DB_NAME", "fakebank"),
                user=os.environ.get("DB_USER", "bankuser"),
                password=os.environ.get("DB_PASS", "bankpass123")
            )
            conn.close()
            print("Database ready.")
            return
        except Exception:
            print("Waiting for database...")
            time.sleep(2)

def seed():
    import os
    wait_for_db()
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", 5432),
        dbname=os.environ.get("DB_NAME", "fakebank"),
        user=os.environ.get("DB_USER", "bankuser"),
        password=os.environ.get("DB_PASS", "bankpass123")
    )
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100),
            aadhaar VARCHAR(14),
            pan VARCHAR(10),
            phone VARCHAR(15),
            email VARCHAR(100),
            upi_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES customers(id),
            account_number VARCHAR(20) UNIQUE,
            ifsc VARCHAR(15),
            account_type VARCHAR(20),
            balance NUMERIC(15,2),
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            account_id INT REFERENCES accounts(id),
            amount NUMERIC(15,2),
            txn_type VARCHAR(20),
            description VARCHAR(200),
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100),
            username VARCHAR(50) UNIQUE,
            password VARCHAR(100),
            role VARCHAR(20)
        );
    """)

    # Seed employees
    employees = [
        ("Rajesh Kumar", "rajesh.kumar", "Pass@1234", "teller"),
        ("Priya Sharma", "priya.sharma", "Secure#456", "branch_manager"),
        ("Amit Verma", "amit.verma", "Bank$789", "auditor"),
        ("admin", "admin", "Admin@2024", "admin"),
    ]
    for emp in employees:
        cur.execute("""
            INSERT INTO employees (full_name, username, password, role)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, emp)

    # Seed 100 customers
    ifsc_codes = ["SBIN0001234", "HDFC0002345", "ICIC0003456", "AXIS0004567", "PUNB0005678"]
    account_types = ["Savings", "Current", "Salary"]

    for _ in range(100):
        name = fake.name()
        aadhaar = fake.numerify("#### #### ####")
        pan = fake.bothify("?????####?").upper()
        phone = fake.phone_number()[:15]
        email = fake.email()
        upi = f"{fake.user_name()}@oksbi"

        cur.execute("""
            INSERT INTO customers (full_name, aadhaar, pan, phone, email, upi_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (name, aadhaar, pan, phone, email, upi))
        customer_id = cur.fetchone()[0]

        acc_number = fake.numerify("####################")
        balance = round(random.uniform(5000, 500000), 2)
        ifsc = random.choice(ifsc_codes)
        acc_type = random.choice(account_types)

        cur.execute("""
            INSERT INTO accounts (customer_id, account_number, ifsc, account_type, balance)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (customer_id, acc_number, ifsc, acc_type, balance))
        account_id = cur.fetchone()[0]

        # 5-10 transactions per account
        for _ in range(random.randint(5, 10)):
            amount = round(random.uniform(100, 50000), 2)
            txn_type = random.choice(["CREDIT", "DEBIT", "UPI", "NEFT", "IMPS"])
            description = fake.sentence(nb_words=5)
            cur.execute("""
                INSERT INTO transactions (account_id, amount, txn_type, description)
                VALUES (%s, %s, %s, %s)
            """, (account_id, amount, txn_type, description))

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding complete. 100 customers, accounts, and transactions created.")

if __name__ == "__main__":
    seed()
