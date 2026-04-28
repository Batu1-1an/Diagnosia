# Contributing to Diagnosia

We welcome contributions! This document outlines how to set up the project for development and the process for submitting changes.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Running Tests](#running-tests)

## Development Setup

### Prerequisites

- Python 3.10+
- A Supabase project ([free tier](https://supabase.com))
- A Google Gemini API key ([get one here](https://ai.google.dev))

### Clone and Install

```bash
git clone https://github.com/Batu1-1an/Diagnosia.git
cd Diagnosia
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Supabase credentials and Google API key.

### Run Migrations

```bash
python backend/run_migrations.py
```

### Start Development Server

```bash
python backend/main.py
```

The app will be available at `http://localhost:5000`.

### Train the ML Model (if needed)

```bash
jupyter notebook notebooks/Medicine\ Recommendation\ System.ipynb
```

## Project Structure

```
backend/         - Flask application (routes, database, migrations)
datasets/        - ML training CSVs and recommendation data
migrations/      - Supabase SQL migrations
models/          - Trained ML models (generated, not committed)
static/          - CSS, images, and frontend assets
templates/       - Jinja2 HTML templates
notebooks/       - Jupyter notebooks for model training
```

## Making Changes

1. **Fork** the repository.
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feat/your-feature
   ```
3. **Make your changes**, keeping them focused on a single concern.
4. **Test your changes** locally before committing.
5. **Commit** using conventional commit format.
6. **Push** and open a Pull Request.

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type       | Usage                          |
|------------|--------------------------------|
| `feat:`    | A new feature                  |
| `fix:`     | A bug fix                      |
| `docs:`    | Documentation changes          |
| `refactor:`| Code changes without fix/feature |
| `chore:`   | Maintenance, deps, tooling     |
| `style:`   | Formatting, whitespace         |
| `test:`    | Adding or fixing tests         |
| `perf:`    | Performance improvements       |
| `security:`| Security fixes                 |

Each commit should be a single logical change. Avoid mixing unrelated changes.

## Pull Request Process

1. Ensure your PR description clearly describes the problem and solution.
2. Reference any related issues.
3. Maintain or increase test coverage.
4. Ensure the app runs without errors locally.
5. A maintainer will review your PR within a reasonable time.

## Coding Standards

- **Python**: Follow PEP 8. Use descriptive variable names.
- **Imports**: Group standard library, third-party, then local imports.
- **Error handling**: Use try/except with specific exception types and log errors with `print()` or a logger.
- **Security**: Never commit secrets, API keys, or `.env` files.
- **Database**: Use Supabase migrations for schema changes.

## Running Tests

```bash
python backend/tests/test_api.py
```

Ensure the development server is running before executing tests.

## Questions?

Open a [GitHub Issue](https://github.com/Batu1-1an/Diagnosia/issues) for bugs, feature requests, or questions.
