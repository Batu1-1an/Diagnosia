# Changelog

## [1.1.0] - 2026-04-28

### Added
- Dockerfile for containerized deployment with gunicorn
- .dockerignore for optimized build contexts
- CONTRIBUTING.md for open source contributors

### Fixed
- `SECRET_KEY` now reads from environment variable instead of generating a random key on every restart, preserving sessions across restarts

### Changed
- Updated `.env.example` with comprehensive documentation for all variables
- Added `gunicorn` to production dependencies

## [1.0.0] - 2024

### Added
- AI-powered medical diagnosis using SVC machine learning model
- Google Gemini Pro chat assistant (Dr.AI) with medical ethics guardrails
- User authentication with Supabase Auth and role-based access (patient, doctor, admin)
- Comprehensive symptom checker with 132 binary features across 41 conditions
- Personalized recommendations (medications, diet, exercise, precautions)
- Doctor review workflow with approval/rejection system
- Radiology module for X-ray image uploads
- Admin dashboard for doctor verification and system management
- Diagnosis history with status tracking
- Responsive glassmorphism UI with Tailwind CSS
- SQL migrations for Supabase PostgreSQL schema
