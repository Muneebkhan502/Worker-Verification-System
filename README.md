# Worker Verification System

A card verification system built for a real client — because in the field, trust shouldn't depend on a phone call to HR. Scan a card, get an answer.

## The problem this solves

Construction sites, inspection companies, and contractors issue physical ID cards to their workers and operators — proof that someone completed training, holds a valid certification, or is authorized to be on-site. The question a supervisor needs answered in the moment is simple: **is this card real, and is it still valid?**

This system gives them that answer in one scan.

## How it works

- An **admin** logs into a dashboard, adds a worker's details (name, card number, Iqama number, company, trade, issue and expiry dates), and the system generates a QR code for that card.
- The QR code is printed and attached to the physical card. It doesn't encode any personal data — just a link to a public verification page.
- Anyone who scans the card lands on that page and can look the worker up by card number, Iqama number, or name.
- If a match exists, they see a clean confirmation with the worker's details and current status. If not, they're told plainly that the record doesn't exist.
- Behind the scenes, a card's status isn't just a label sitting in a database — expiry is computed in real time, so a card doesn't quietly stay "Active" after its date has passed.

## Features

- **Admin dashboard** — at-a-glance counts of total, active, suspended, cancelled, and expired workers
- **Full worker management** — create, search, view, edit, and delete records
- **Public verification page** — no login required, built for the person standing at the gate with a phone in hand
- **QR code generation** — downloadable as PNG or print-ready SVG
- **Session-based authentication** — the admin panel is locked down; the verification page stays open to everyone
- **Real-time expiry logic** — a card's displayed status reflects today's date, not just what was last saved

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Database | PostgreSQL + SQLAlchemy 2.0 |
| Validation | Pydantic |
| Templating | Jinja2 |
| Frontend | Bootstrap 5 + vanilla JavaScript (fetch API) |
| Auth | Session cookies + bcrypt password hashing |
| QR generation | `qrcode` |

## Project structure

```
.
├── main.py              # routes
├── models.py             # SQLAlchemy models (Worker, WorkerStatus)
├── schemas.py             # Pydantic schemas
├── services.py            # business logic (WorkerManager)
├── database.py            # DB engine & session setup
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── dashboard.html
│   ├── workers.html
│   ├── add_worker.html
│   ├── update_worker.html
│   ├── view_worker.html
│   ├── verify.html
│   └── login.html
└── requirements.txt
```

## Running it locally

**1. Clone and set up a virtual environment**
```bash
git clone https://github.com/<Muneebkhan502>/Worker-Verification-System.git
cd Worker-Verification-System
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Set up your environment variables**

Create a `.env` file in the project root:
```
SECRET_KEY=a-long-random-string
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-admin-password
VERIFY_URL=http://127.0.0.1:8000/verify-page
DATABASE_URL=postgresql://user:password@localhost/worker_db
```

**4. Run the server**
```bash
fastapi dev main.py
```

Visit `http://127.0.0.1:8000` for the admin dashboard, or `http://127.0.0.1:8000/verify-page` for the public verification page.

## A note on the QR codes

Every QR code encodes the same thing: the public verification page's URL — nothing worker-specific. This was a deliberate choice. It keeps the card itself free of embedded personal data, and it means a lost or copied QR code reveals nothing on its own; the lookup still has to happen against the live database.

## Status

This is a live client project, built and shipped feature by feature — dashboard, CRUD, search, QR generation, and authentication are complete. Built as my first paid freelance project, with an eye toward the kind of backend work I want to keep doing: FastAPI, real databases, and systems that hold up under actual use.

---

*Built with FastAPI, PostgreSQL, and a lot of debugging sessions.*
