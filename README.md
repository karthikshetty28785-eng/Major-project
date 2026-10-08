# 🏦 Hash-Trap Forensics (HTF) — Honeypot Banking System

**Automated Forensic Engine for Digital Evidence Preservation in Banking Systems**

> Final Year Major Project | CSBS Dept | NMIT Bangalore | AY 2025–2026  
> **Team:** Karthik S Shetty (1NT23CB023) · Anu V (1NT23CB007) · Abhijna S P (1NT23CB002)  
> **Guide:** Prof. Manohar R

---

## 📁 Project Structure
Major-project/
├── docker-compose.yml ← Orchestrates honeypot + PostgreSQL containers
├── honeypot/
│ ├── app.py ← Main Flask web app (fake SecureBank portal)
│ ├── seed.py ← Seeds 100 fake Indian customer records into DB
│ ├── Dockerfile ← Docker image for the Flask app
│ ├── requirements.txt ← Python dependencies
│ └── templates/
│ ├── login.html ← Fake bank login page
│ ├── dashboard.html ← Customer dashboard
│ ├── transactions.html ← Transaction history
│ └── admin.html ← Admin panel (restricted)
└── oob/
└── recorder.py ← Out-of-band session recorder (runs on host)


---

## ⚙️ Prerequisites

Install these before starting:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (must be running)
- [Python 3.11+](https://www.python.org/downloads/)
- Git

---

## 🚀 Setup & Run (Step by Step)

### Step 1 — Clone the repository

```bash
git clone https://github.com/kartikshetty28785-eng/Major-project.git
cd Major-project
```

### Step 2 — Create the .env file (required — not in repo for security)

Inside the `honeypot/` folder, create a file named `.env` with this content:
POSTGRES_USER=htf_user
POSTGRES_PASSWORD=htf_pass
POSTGRES_DB=htf_db
DATABASE_URL=postgresql://htf_user:htf_pass@db:5432/htf_db
SECRET_KEY=supersecretkey123


```bash
# On Linux/Mac/WSL:
cat > honeypot/.env << 'EOF'
POSTGRES_USER=htf_user
POSTGRES_PASSWORD=htf_pass
POSTGRES_DB=htf_db
DATABASE_URL=postgresql://htf_user:htf_pass@db:5432/htf_db
SECRET_KEY=supersecretkey123
EOF
```

### Step 3 — Build and start Docker containers

```bash
docker compose up --build -d
```

Wait about 30 seconds for PostgreSQL to fully start.

### Step 4 — Seed the database (first time only)

```bash
docker exec honeypot_app python seed.py
```

You should see: `Seeded 100 customers successfully.`

### Step 5 — Set up Python environment for OOB recorder

```bash
python3 -m venv htf-env
source htf-env/bin/activate        # On Windows WSL: same command
pip install flask psycopg2-binary faker python-dotenv docker requests
```

### Step 6 — Start the OOB recorder (open a new terminal)

```bash
source htf-env/bin/activate
python3 oob/recorder.py
```

Leave this terminal running. It captures all attacker sessions in real time.

### Step 7 — Open the honeypot in browser
http://localhost:5000


---

## 🔑 Test Login Credentials

| Username | Password | Role |
|---|---|---|
| rajesh.kumar | Pass@1234 | teller |
| priya.sharma | Secure#456 | branch_manager |
| amit.verma | Bank$789 | auditor |
| admin | Admin@2024 | admin |

---

## 🍯 Trigger the Honeytoken

While logged in, visit this URL in the browser:


Then check the alert log:

```bash
cat oob/honeytoken_alerts.log
```

You should see a `[CRITICAL]` alert with timestamp and session details.

---

## 📋 Check Captured Sessions

```bash
cat oob/captured_sessions.log
```

---

## 🛑 Stop the Project

```bash
docker compose down
```

To also delete all database data (full reset):

```bash
docker compose down -v
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `docker compose` command not found | Use `docker-compose` (with hyphen) instead |
| Permission denied on docker socket | Run with `sudo docker compose ...` |
| Port 5000 already in use | Run `sudo lsof -i :5000` and kill that process |
| `seed.py` fails with connection error | Wait 30 more seconds and retry — DB is still starting |
| OOB recorder shows import error | Make sure venv is activated: `source htf-env/bin/activate` |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Web App | Flask (Python 3.11) |
| Database | PostgreSQL 15 |
| Containerization | Docker + Docker Compose |
| Data Generation | Faker (en_IN locale) |
| OOB Recording | Python sockets + Docker SDK |
| Hashing | TLSH fuzzy hashing |
| Blockchain Anchor | Ethereum Sepolia (planned) |

---

*NMIT Bangalore — Department of Computer Science and Business Systems*
