<div align="center">
  <img src="static/doctor-ai.png" alt="Diagnosia" width="110" style="border-radius: 20px;">
  <h1>Diagnosia</h1>
  <p><strong>AI-Powered Medical Symptom Checker &amp; Diagnosis Assistant</strong></p>
  <p>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
    <img src="https://img.shields.io/badge/Framework-Flask-000000?style=flat-square&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/ML-SVC-orange?style=flat-square&logo=scikit-learn&logoColor=white" alt="SVC">
    <img src="https://img.shields.io/badge/AI-Gemini%20Pro-8E75B2?style=flat-square&logo=google" alt="Gemini Pro">
    <img src="https://img.shields.io/badge/Database-Supabase-3ECF8E?style=flat-square&logo=supabase" alt="Supabase">
    <img src="https://img.shields.io/badge/style-Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss" alt="Tailwind CSS">
  </p>
  <br>
</div>

Diagnosia is a full-stack web application that combines **machine learning** with **generative AI** to deliver preliminary health assessments. Patients input symptoms, receive instant disease predictions from a trained Support Vector Classifier (SVC), and get personalized recommendations for medications, diet, exercise, and precautions. An integrated **Dr.AI** chat assistant (powered by Google Gemini Pro) offers conversational medical guidance, while a **doctor review workflow** allows verified medical professionals to review, approve, or reject diagnoses.

---

## Why Diagnosia?

Millions of people lack immediate access to medical professionals for minor health concerns. Diagnosia bridges that gap — not as a replacement for doctors, but as an intelligent **first-pass triage system**. It is built for:

| Audience | Benefit |
|----------|---------|
| **Patients** | Get instant, data-driven insights about symptoms before seeing a doctor |
| **Doctors** | Review AI-generated diagnoses, approve or reject them with clinical notes |
| **Administrators** | Verify medical professionals and oversee the review pipeline |
| **Developers** | Extend the platform with new ML models, datasets, or radiology modules |

The system respects medical ethics at every layer: Dr.AI is guardrailed with safety prompts, diagnoses are human-reviewable, and patient data is protected by Supabase Row-Level Security.

---

## Features

| Feature | Description | Tech |
|---------|-------------|------|
| **ML-Powered Diagnosis** | Predict diseases from 132 binary symptoms across 41 conditions | scikit-learn SVC |
| **Dr.AI Chat Assistant** | Conversational AI with medical ethics guardrails & safety settings | Google Gemini Pro |
| **Personalized Regimen** | Auto-generated medications, diets, exercise plans & precautions per disease | Pandas datasets |
| **Doctor Review Workflow** | Request a doctor review; doctors approve/reject with clinical notes | Supabase RLS |
| **Radiology Upload** | X-ray image upload (extensible for future AI analysis) | HTML5 / Flask |
| **Role-Based Access** | Three-tier: Patient, Doctor (verified), Admin | Supabase Auth + RLS |
| **Admin Dashboard** | Doctor registration verification & system management | Flask + Tailwind |
| **Diagnosis History** | Full timeline with status tracking (pending, approved, rejected) | Supabase JSONB |
| **Responsive Design** | Glassmorphism UI across desktop & mobile | Tailwind CSS |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Client Browser                                   │
│  ┌───────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────────────────┐ │
│  │ Diagnosis │  │ Symptom Form │  │ Dr.AI    │  │ Doctor / Admin Dash. │ │
│  │ Page      │  │ (132 sxs)    │  │ Chat     │  │                       │ │
│  └─────┬─────┘  └──────┬───────┘  └────┬─────┘  └──────────┬────────────┘ │
│        │               │               │                   │              │
└────────┼───────────────┼───────────────┼───────────────────┼──────────────┘
         │               │               │                   │
         ▼               ▼               ▼                   ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              Flask 3.0 (backend/main.py)                    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         Route Handlers                                │  │
│  │  /diagnosis  /chat  /request_approval  /doctor/approve  /admin/*      │  │
│  └────────┬───────────┬────────────────────┬──────────────────┬──────────┘  │
│           │           │                    │                  │             │
│           ▼           ▼                    ▼                  ▼             │
│  ┌────────────┐ ┌──────────┐ ┌──────────────────┐ ┌─────────────────────┐  │
│  │  SVC Model │ │ Gemini   │ │  Supabase Auth   │ │  Session Manager   │  │
│  │  (svc.pkl) │ │ Pro API  │ │  + RLS Policies  │ │  (Flask-Login)     │  │
│  └──────┬─────┘ └────┬─────┘ └────────┬─────────┘ └─────────────────────┘  │
│         │            │                │                                     │
└─────────┼────────────┼────────────────┼─────────────────────────────────────┘
          │            │                │
          ▼            ▼                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           Data Layer                                       │
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐                          │
│  │  Supabase PostgreSQL│  │  Datasets (CSV)     │                          │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │                          │
│  │  │ profiles      │  │  │  │ description   │  │                          │
│  │  │ diagnoses     │  │  │  │ medications   │  │                          │
│  │  │ chat_reviews  │  │  │  │ diets         │  │                          │
│  │  └───────────────┘  │  │  │ workout_df    │  │                          │
│  └─────────────────────┘  │  │ precautions   │  │                          │
│                            │  └───────────────┘  │                          │
│                            └─────────────────────┘                          │
└────────────────────────────────────────────────────────────────────────────┘
```

**Data flow:**

1. User selects symptoms on the diagnosis page → binary symptom vector (length 132)
2. Flask sends vector to the **SVC model** (`models/svc.pkl`) → predicted disease class
3. Supporting CSV datasets hydrate **personalized recommendations**
4. All records persist to **Supabase** (PostgreSQL + RLS) for history & review
5. Dr.AI chat requests route through Flask to **Gemini Pro** with medical-context system prompt
6. Doctors authenticate, view assigned cases, and approve/reject via Supabase queries

---

## Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center"><strong>🏠 Dashboard</strong><br><sub>Sacred-geometry hero, CTA &amp; feature overview</sub><br><br><code>📸 [screenshot]</code></td>
      <td align="center"><strong>🔬 Diagnosis</strong><br><sub>Symptom selector, live predictions &amp; recommendations</sub><br><br><code>📸 [screenshot]</code></td>
    </tr>
    <tr>
      <td align="center"><strong>🤖 Dr.AI Chat</strong><br><sub>Conversational AI with medical guardrails</sub><br><br><code>📸 [screenshot]</code></td>
      <td align="center"><strong>👨‍⚕️ Doctor Dashboard</strong><br><sub>Case list, statistics &amp; review queue</sub><br><br><code>📸 [screenshot]</code></td>
    </tr>
  </table>
</div>

---

## Quick Start

<details>
<summary><strong>Click to expand</strong></summary>

### Prerequisites

- Python 3.10+
- A Supabase project ([free tier](https://supabase.com))
- A Google Gemini API key ([get one here](https://ai.google.dev))

### 1. Clone

```bash
git clone https://github.com/Batu1-1an/Diagnosia.git
cd Diagnosia
```

### 2. Virtual environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon / public key |
| `GOOGLE_API_KEY` | Google Gemini Pro API key |
| `SECRET_KEY` | Flask secret key (random string) |

### 5. Run database migrations

```bash
python backend/run_migrations.py
```

Or apply `migrations/*.sql` manually via the Supabase SQL editor.

### 6. Start the server

```bash
python backend/main.py
```

The app is now available at **http://localhost:5000**.

> **Note:** If `models/svc.pkl` is missing, re-train via the Jupyter notebook: `jupyter notebook notebooks/Medicine\ Recommendation\ System.ipynb`

</details>

---

## Usage

1. **Register** — Create a patient account or register as a doctor (requires admin verification)
2. **Diagnosis** — Select symptoms from the 132-feature panel → submit for ML prediction
3. **Dr.AI Chat** — Discuss your symptoms with the Gemini Pro–powered assistant
4. **Request Review** — Choose a verified doctor to review your diagnosis
5. **History** — Track all past diagnoses and their review status (pending / approved / rejected)
6. **Doctor Dashboard** — Review assigned cases, approve or reject with clinical notes
7. **Admin Dashboard** — Verify new doctor registrations and manage the platform

---

## API Reference

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Landing page |
| POST | `/predict` | Legacy single-disease prediction |
| GET/POST | `/diagnosis` | Full diagnosis with recommendations |
| POST | `/chat` | Dr.AI chat message (Gemini Pro) |
| POST | `/request_approval` | Submit diagnosis for doctor review |
| POST | `/request_chat_approval` | Submit Dr.AI chat for doctor review |
| POST | `/assign_doctor/<id>` | Assign a doctor to a diagnosis |
| POST | `/unassign_doctor/<id>` | Remove a doctor assignment |
| POST | `/doctor/approve/<id>` | Approve or reject a diagnosis |
| POST | `/doctor/review_chat/<id>` | Review a Dr.AI chat transcript |
| GET | `/doctor/dashboard` | Doctor case management dashboard |
| GET | `/admin/dashboard` | Admin panel |
| POST | `/admin/verify-doctor/<id>` | Verify or reject a doctor registration |
| GET | `/history` | Patient diagnosis history |
| GET | `/profile` | User profile page |
| GET/POST | `/radiology` | X-ray image upload (placeholder) |
| GET/POST | `/register` | Patient / doctor registration |
| GET/POST | `/login` | Authentication |
| GET | `/logout` | Session termination |

---

## ML Model

| Property | Detail |
|----------|--------|
| **Algorithm** | Support Vector Classifier (SVC) |
| **Symptom Features** | 132 binary (present / absent) |
| **Disease Classes** | 41 conditions (Malaria, Typhoid, Diabetes, GERD, Pneumonia, …) |
| **Training Set** | `datasets/Training.csv` — 4,920 labeled samples |
| **Serialized Model** | `models/svc.pkl` |
| **Supporting Data** | `description.csv`, `medications.csv`, `diets.csv`, `workout_df.csv`, `precautions_df.csv` |
| **Notebook** | `notebooks/Medicine Recommendation System.ipynb` |

---

## Database Schema

### `profiles`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Auth user ID |
| `name` | TEXT | Full name |
| `email` | TEXT (unique) | Email address |
| `role` | TEXT | `user`, `doctor`, or `admin` |
| `is_verified` | BOOLEAN | Doctor verification status |
| `license_number` | TEXT | Medical license number (doctors) |
| `specialization` | TEXT | Medical specialization |

### `diagnoses`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Auto-generated |
| `user_id` | UUID (FK) | Patient |
| `doctor_id` | UUID (FK, nullable) | Assigned reviewing doctor |
| `symptoms` | JSONB | Symptom array |
| `disease` | TEXT | Predicted disease |
| `medications` | JSONB | Recommended medications |
| `diet` | JSONB | Diet recommendations |
| `workout` | TEXT | Exercise recommendation |
| `precautions` | JSONB | Precaution list |
| `status` | TEXT | `pending`, `pending_review`, `approved`, `rejected` |
| `doctor_notes` | TEXT | Doctor feedback |

### `chat_reviews`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Auto-generated |
| `user_id` | UUID (FK) | Patient |
| `doctor_id` | UUID (FK) | Doctor |
| `chat_history` | JSONB | Dr.AI conversation transcript |
| `status` | TEXT | `pending`, `approved`, `rejected` |
| `doctor_notes` | TEXT | Doctor feedback |

---

## Security

- **Row-Level Security (RLS)** on all Supabase tables — patients see only their own data
- **Role isolation** — doctors access only assigned cases; admins manage verification only
- **Session authentication** — Supabase Auth with Flask session management
- **Input sanitization** — Flask request validation and CSRF protection
- **AI guardrails** — Gemini Pro system prompt with medical-ethics constraints

---

## Project Structure

```
Diagnosia/
├── backend/                      # Python application backend
│   ├── main.py                   # Flask entry point & route definitions
│   ├── database.py               # Supabase client initialization
│   ├── run_migrations.py         # Migration runner (DDL)
│   ├── fix_doctor_assignments.py # Doctor assignment repair utility
│   ├── fix_jsonb.py              # JSONB data migration script
│   └── tests/
│       └── test_api.py           # API integration tests
│
├── datasets/                     # ML training & recommendation CSVs
│   ├── Training.csv              # 4,920 labeled symptom→disease samples
│   ├── Symptom-severity.csv      # Severity mapping per symptom
│   ├── symtoms_df.csv            # Symptom descriptions
│   ├── description.csv           # Disease descriptions
│   ├── medications.csv           # Per-disease medication lists
│   ├── diets.csv                 # Per-disease diet plans
│   ├── workout_df.csv            # Per-disease exercise regimens
│   └── precautions_df.csv        # Per-disease precaution lists
│
├── docs/
│   └── CHANGELOG.md              # Version history
│
├── migrations/                   # Supabase SQL migrations
│   ├── create_tables.sql         # profiles & diagnoses DDL
│   ├── create_chat_reviews.sql   # chat_reviews table + RLS
│   ├── setup_rls.sql             # Row-level security policies
│   ├── add_foreign_keys.sql      # FK constraint definitions
│   └── fix_jsonb_data.sql        # JSONB data migration
│
├── models/
│   └── svc.pkl                   # Trained SVC classifier
│
├── notebooks/
│   └── Medicine Recommendation System.ipynb  # Model training notebook
│
├── static/                       # Public assets
│   ├── doctor-ai.png             # Dr.AI avatar
│   ├── grid.svg / dots.svg       # Background patterns
│   └── img/
│
├── templates/                    # Jinja2 HTML templates
│   ├── base.html                 # Layout shell & navigation
│   ├── index.html                # Landing page
│   ├── diagnosis.html            # Symptom checker + Dr.AI
│   ├── history.html              # Diagnosis history
│   ├── doctor_dashboard.html     # Doctor case management
│   ├── admin_dashboard.html      # Admin verification panel
│   ├── profile.html              # User profile
│   ├── radiology.html            # X-ray upload (WIP)
│   ├── about.html / contact.html / blog.html / developer.html
│   └── login.html / register.html / register_doctor.html
│
├── .env.example                  # Environment variable template
├── .gitignore
├── LICENSE                       # MIT License
├── README.md
├── package.json
├── requirements.txt              # Python dependencies
└── tailwind.config.js            # Tailwind CSS configuration
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create a feature branch** — `git checkout -b feat/your-feature`
3. **Commit your changes** — `git commit -m "feat: add your feature"`
4. **Push** — `git push origin feat/your-feature`
5. **Open a Pull Request**

Please ensure your code passes existing tests and follows the project's coding conventions. For major changes, open an issue first to discuss what you would like to change.

---

## License

<div align="center">
  <p>
    This project is <a href="LICENSE">MIT Licensed</a> —
    Copyright &copy; 2025 <strong>Batu1-1an</strong>
  </p>
  <p>
    <sub>Built with ❤️ for accessible, AI-assisted healthcare triage.</sub>
  </p>
</div>
