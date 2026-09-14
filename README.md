# VOID — Versatile Orchestrated Intelligent Dispatcher

> A governed AI execution platform. Turn human intent into controlled, validated, observable outcomes.

---

## What is VOID?

VOID is a local-first AI command center that sits between you and AI models/agents. Instead of running uncontrolled AI, every request flows through a structured execution layer:

1. **Intent Gate** — Validates and classifies your intent
2. **Strategy Resolver** — Selects AUTO, GUIDED, or MANUAL execution
3. **Policy Enforcement** — Applies project-level rules before dispatch
4. **Execution Fabric** — Coordinates agents, models, tools, and workflows
5. **Validation & Evidence** — Produces verifiable, traceable outputs

---

## Repository Structure

```
void/
├── apps/
│   ├── backend/                  # FastAPI backend (Python)
│   │   ├── app/
│   │   │   ├── api/              # Route controllers & dependencies
│   │   │   │   ├── v1/           # Versioned API endpoints
│   │   │   │   └── deps.py       # Shared dependencies (auth, DB)
│   │   │   ├── capabilities/     # Pluggable AI capabilities (resume/JD, etc.)
│   │   │   ├── core/             # Config, security, JWT
│   │   │   ├── db/               # Database session factory
│   │   │   ├── execution/        # Task state machine
│   │   │   ├── middleware/       # Audit logging middleware
│   │   │   ├── models/           # SQLAlchemy ORM models
│   │   │   ├── repositories/     # Data access layer
│   │   │   ├── schemas/          # Pydantic request/response models
│   │   │   ├── services/         # Business logic
│   │   │   └── main.py           # FastAPI application entrypoint
│   │   ├── alembic/              # Database migrations
│   │   ├── scripts/              # Utility scripts
│   │   ├── tests/                # Pytest test suite
│   │   ├── alembic.ini
│   │   ├── pytest.ini
│   │   └── requirements.txt
│   │
│   └── frontend/                 # Next.js frontend (TypeScript)
│       ├── src/
│       │   ├── app/              # Next.js App Router pages
│       │   │   ├── (auth)/       # Auth route group (sign-in, sign-up, etc.)
│       │   │   ├── onboarding/   # First-time setup
│       │   │   ├── workspace/    # Main dashboard
│       │   │   ├── layout.tsx    # Root layout
│       │   │   └── page.tsx      # Landing page
│       │   ├── components/       # Reusable UI components
│       │   │   ├── layout/       # AppShell, Sidebar, Topbar
│       │   │   └── ui/           # MetricCard, MissionCard, CommandPanel
│       │   └── types/            # Shared TypeScript types
│       ├── __tests__/            # Vitest test suite
│       ├── package.json
│       └── tsconfig.json
│
├── docs/                         # Project documentation
│   ├── API.md                    # API reference
│   ├── ARCHITECTURE.md           # System design
│   ├── DEVELOPMENT.md            # Dev setup guide
│   ├── SECURITY.md               # Security model
│   └── TESTING.md                # Testing strategy
│
├── storage/                      # Runtime file storage (gitignored)
│   ├── artifacts/
│   ├── uploads/
│   └── temporary/
│
├── .env.example                  # Environment variable template
├── .gitignore
├── CHANGELOG.md
└── README.md
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git

### 1. Clone & Setup

```bash
git clone https://github.com/shivaganesh720/void.git
cd void
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r apps/backend/requirements.txt

# Copy environment config
cp .env.example .env

# Run database migrations
cd apps/backend
alembic upgrade head
cd ../..
```

### 3. Frontend Setup

```bash
cd apps/frontend
npm install
cd ../..
```

### 4. Run — Development Mode

**Terminal 1 — Backend:**

```powershell
$env:PYTHONPATH = "apps\backend"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir apps\backend --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**

```powershell
cd apps\frontend
$env:NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000"
npm run dev
```

Open **http://localhost:3000**

---

## API Endpoints

| Category  | Base Path                         |
| --------- | --------------------------------- |
| Auth      | `POST /api/v1/auth/login`         |
| Auth      | `POST /api/v1/auth/register`      |
| Auth      | `POST /api/v1/auth/logout`        |
| Auth      | `GET  /api/v1/auth/me`            |
| Projects  | `GET/POST /api/v1/projects`       |
| Missions  | `POST /api/v1/missions/universal` |
| Missions  | `GET  /api/v1/missions/{id}`      |
| Dashboard | `GET  /api/v1/dashboard/summary`  |
| Health    | `GET  /health/ready`              |

Full reference: [`docs/API.md`](docs/API.md)

---

## Security Model

- **HttpOnly cookies** for `void_access_token` and `void_refresh_token`
- **Refresh token rotation** with reuse detection
- **Project-scoped RBAC** (OWNER / ADMIN / MEMBER / VIEWER)
- **Policy enforcement** before every mission dispatch
- **Audit trail** for all state-changing events
- **CORS** restricted to `http://localhost:3000` in dev

Full details: [`docs/SECURITY.md`](docs/SECURITY.md)

---

## Tech Stack

| Layer      | Technology                                 |
| ---------- | ------------------------------------------ |
| Backend    | FastAPI, SQLAlchemy, Alembic, SQLite (dev) |
| Auth       | JWT (access + refresh), HttpOnly cookies   |
| Frontend   | Next.js 16, React 19, TypeScript           |
| Animations | Framer Motion                              |
| Icons      | Lucide React                               |
| Testing    | Pytest (backend), Vitest (frontend)        |

---

## License

MIT — see [LICENSE](LICENSE) for details.
