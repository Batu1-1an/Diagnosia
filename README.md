<p align="center">
  <img src="static/doctor-ai.png" alt="Diagnosia Logo" width="120">
</p>

<h1 align="center">Diagnosia</h1>

<p align="center">
  <strong>AI-Powered Medical Symptom Checker &amp; Diagnosis Assistant</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Framework-Flask-000000?logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/ML-SVC-orange?logo=scikit-learn" alt="SVC">
  <img src="https://img.shields.io/badge/AI-Gemini%20Pro-8E75B2?logo=google" alt="Gemini Pro">
  <img src="https://img.shields.io/badge/Database-Supabase-3ECF8E?logo=supabase" alt="Supabase">
  <img src="https://img.shields.io/badge/style-Tailwind%20CSS-06B6D4?logo=tailwindcss" alt="Tailwind CSS">
</p>

---

Diagnosia is a full-stack web application that uses **machine learning** and **generative AI** to provide preliminary health assessments. Patients input their symptoms, receive an instant disease prediction powered by a Support Vector Classifier (SVC) model, and get personalized recommendations for medications, diet, exercise, and precautions. An integrated **Dr.AI** chat assistant (powered by Google Gemini Pro) offers conversational medical guidance, and a **doctor review workflow** allows verified medical professionals to review, approve, or reject diagnoses.

---

## Features

- **🔬 ML-Powered Diagnosis** — Predicts diseases from 132 symptoms across 41 conditions using a trained SVC model
- **🤖 Dr.AI Chat Assistant** — Conversational AI powered by Google Gemini Pro with medical ethics guardrails
- **👨‍⚕️ Doctor Review Workflow** — Patients can request review; doctors approve/reject with notes
- **📋 Personalized Recommendations** — Medications, diet plans, exercise routines, and precautions for each diagnosis
- **📊 Diagnosis History** — Full history with status tracking (pending, approved, rejected)
- **🩻 Radiology Upload** — X-ray image upload for future AI analysis (extensible)
- **🔐 Role-Based Access** — Three roles: Patient, Doctor (verified), Admin
- **🛡️ Admin Dashboard** — Doctor registration verification and system management
- **📱 Responsive Design** — Glassmorphism UI with Tailwind CSS, works on desktop and mobile

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, Flask 3.0 |
| **Database** | Supabase (PostgreSQL + Auth + Row-Level Security) |
| **ML Model** | Scikit-learn SVC (Support Vector Classifier) |
| **AI** | Google Generative AI (Gemini Pro) |
| **Frontend** | Tailwind CSS, JavaScript, Font Awesome |
| **Data** | Pandas, NumPy |
| **Environment** | python-dotenv |

## ML Model

The core diagnosis engine uses a **Support Vector Classifier (SVC)** trained on a symptom–disease dataset.

| Property | Detail |
|----------|--------|
| **Algorithm** | Support Vector Classifier (SVC) |
| **Symptoms** | 132 binary symptom features |
| **Diseases** | 41 conditions (e.g., Malaria, Typhoid, Diabetes, GERD, Pneumonia) |
| **Training Data** | `datasets/Training.csv` — 4,920 labeled samples |
| **Model File** | `models/svc.pkl` (serialized via pickle) |
| **Supporting Data** | `description.csv`, `medications.csv`, `diets.csv`, `workout_df.csv`, `precautions_df.csv` |
| **Notebook** | `notebooks/Medicine Recommendation System.ipynb` |

The pipeline:
1. User selects symptoms → binary vector of length 132
2. SVC predicts disease class
3. Supporting datasets provide description, medications, diet, workout, and precautions

## Prerequisites

- Python 3.10+
- A Supabase project (free tier works)
- A Google Gemini API key

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Batu1-1an/Diagnosia.git
cd Diagnosia
```

### 2. Create and activate a virtual environment

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

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon/public key |
| `GOOGLE_API_KEY` | Google Gemini API key |

### 5. Run database migrations

Migrations set up the `profiles`, `diagnoses`, and `chat_reviews` tables with RLS policies.

```bash
python run_migrations.py
```

Or apply `migrations/*.sql` manually via the Supabase SQL editor.

### 6. Train the ML model (optional)

If `models/svc.pkl` is missing, run the Jupyter notebook:

```bash
jupyter notebook notebooks/Medicine\ Recommendation\ System.ipynb
```

### 7. Start the server

```bash
python main.py
```

The app runs at `http://localhost:5000`.

## Usage

1. **Register** — Create a patient account or register as a doctor
2. **Diagnosis** — Select symptoms and submit for ML prediction
3. **Dr.AI Chat** — Discuss your symptoms with the AI assistant
4. **Request Review** — Choose a verified doctor to review your diagnosis
5. **History** — Track all past diagnoses and their review status
6. **Doctor Dashboard** — (doctors) Review assigned cases, approve/reject with notes
7. **Admin Dashboard** — (admins) Verify newly registered doctors

### Screenshots

| Page | Description |
|------|-------------|
| Home | Hero section with sacred-geometry animations and CTA |
| Diagnosis | Symptom selector, Dr.AI chat, analysis results with recommendations |
| Doctor Dashboard | Case list, statistics, pending reviews |
| Admin Dashboard | Doctor verification queue |

*(Screenshots to be added)*

## Project Structure

```
Diagnosia/
├── main.py                     # Flask application entry point
├── database.py                 # Supabase client initialization
├── run_migrations.py           # Database migration runner
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore
├── LICENSE                     # MIT License
├── CHANGELOG.md
│
├── datasets/                   # ML training & recommendation data
│   ├── Training.csv            # SVC training data (4920 samples)
│   ├── Symptom-severity.csv    # Symptom severity mapping
│   ├── symtoms_df.csv          # Symptom descriptions
│   ├── description.csv         # Disease descriptions
│   ├── medications.csv         # Recommended medications per disease
│   ├── diets.csv               # Diet recommendations per disease
│   ├── workout_df.csv          # Exercise recommendations per disease
│   └── precautions_df.csv      # Precautions per disease
│
├── models/                     # Serialized ML models
│   └── svc.pkl                 # Trained SVC classifier
│
├── migrations/                 # SQL migration files
│   ├── create_tables.sql       # Profiles & diagnoses tables
│   ├── create_chat_reviews.sql # Chat review table + RLS
│   ├── setup_rls.sql           # Row-level security policies
│   ├── add_foreign_keys.sql    # Foreign key constraints
│   ├── fix_jsonb_data.sql      # JSONB data fix scripts
│   └── ...
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with navigation
│   ├── index.html              # Landing page with hero
│   ├── diagnosis.html          # Symptom checker + Dr.AI chat
│   ├── history.html            # Diagnosis history
│   ├── doctor_dashboard.html   # Doctor case management
│   ├── admin_dashboard.html    # Admin verification panel
│   ├── profile.html            # User profile management
│   ├── radiology.html          # X-ray upload (placeholder)
│   ├── about.html / contact.html / blog.html / developer.html
│   ├── login.html / register.html / register_doctor.html
│   └── history_new.html
│
├── static/                     # Static assets
│   ├── doctor-ai.png           # Dr.AI avatar
│   ├── grid.svg / dots.svg     # Background patterns
│   └── img/
│
└── notebooks/                  # Jupyter notebooks
    └── Medicine Recommendation System.ipynb
```

## Database Schema

### `profiles`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Auth user ID |
| `name` | TEXT | Full name |
| `email` | TEXT (unique) | Email address |
| `role` | TEXT | `user`, `doctor`, or `admin` |
| `is_verified` | BOOLEAN | Doctor verification status |
| `license_number` | TEXT | Medical license (doctors) |
| `specialization` | TEXT | Medical specialization |

### `diagnoses`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID (PK) | Auto-generated |
| `user_id` | UUID (FK) | Patient |
| `doctor_id` | UUID (FK, nullable) | Assigned doctor |
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
| `chat_history` | JSONB | Dr.AI conversation |
| `status` | TEXT | `pending`, `approved`, `rejected` |
| `doctor_notes` | TEXT | Doctor feedback |

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/` | Home page |
| GET/POST | `/predict` | Initial diagnosis (legacy) |
| GET/POST | `/diagnosis` | Full diagnosis with recommendations |
| POST | `/chat` | Dr.AI chat (Gemini Pro) |
| POST | `/request_approval` | Submit diagnosis for doctor review |
| POST | `/request_chat_approval` | Submit chat for doctor review |
| POST | `/assign_doctor/<id>` | Assign doctor to diagnosis |
| POST | `/unassign_doctor/<id>` | Remove doctor assignment |
| POST | `/doctor/approve/<id>` | Doctor approves/rejects diagnosis |
| POST | `/doctor/review_chat/<id>` | Doctor reviews chat |
| GET | `/doctor/dashboard` | Doctor case dashboard |
| GET | `/admin/dashboard` | Admin panel |
| POST | `/admin/verify-doctor/<id>` | Admin verifies/rejects doctor |
| GET | `/history` | Patient diagnosis history |
| GET | `/profile` | User profile |
| GET/POST | `/radiology` | X-ray upload (placeholder) |
| GET/POST | `/register` / `/login` / `/logout` | Authentication |

## Security

- **Row-Level Security (RLS)** on all Supabase tables
- Patients see only their own diagnoses
- Doctors see only assigned cases
- Session-based authentication via Supabase Auth
- Input sanitization and CSRF protection via Flask

## License

[MIT](LICENSE) — Copyright (c) 2025 Batu1-1an
