# Diagnosia - Medical Symptom Checker & Diagnosis Assistant

## Description

Diagnosia is a web application designed to assist users in identifying potential medical conditions based on their symptoms. It provides preliminary diagnoses using a machine learning model and facilitates interaction between patients and doctors for review and consultation.

## Key Features

*   **User Authentication:** Secure registration and login for patients and doctors.
*   **Symptom Checker:** Users can input their symptoms to receive a potential diagnosis prediction.
*   **Diagnosis History:** Patients can view their past diagnoses and their status (pending, approved, rejected).
*   **AI Chat Assistant:** Integration with Google Gemini for preliminary medical advice (Dr.AI).
*   **Doctor Portal:**
    *   Doctors can register and get verified by an admin.
    *   View assigned diagnoses and chat reviews.
    *   Approve or reject diagnoses with notes.
    *   Review chat histories.
*   **Admin Dashboard:** Manage doctor verifications.
*   **Profile Management:** Users can update their profile information.
*   **Radiology Upload (Placeholder):** Functionality to upload X-ray images (analysis logic TBD).

## Technology Stack

*   **Backend:** Python, Flask
*   **Database:** Supabase (PostgreSQL)
*   **Machine Learning:** Scikit-learn (SVC model), Pandas, NumPy
*   **AI Integration:** Google Generative AI (Gemini Pro)
*   **Frontend:** HTML, CSS (likely Tailwind CSS based on `tailwind.config.js`), JavaScript
*   **Environment Management:** `python-dotenv`

## Machine Learning Model

The core diagnosis prediction relies on a **Support Vector Classifier (SVC)** model trained on a dataset correlating symptoms to diseases.

*   **Model:** The pre-trained SVC model is loaded from `models/svc.pkl`.
*   **Input:** The model takes a vector representing the presence or absence of various symptoms selected by the user.
*   **Output:** It predicts the most likely disease based on the input symptom vector.
*   **Datasets:** The model was likely trained using data from the `datasets/` directory (e.g., `Training.csv`, `Symptom-severity.csv`).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Batu1-1an/Diagnosia.git
    cd Diagnosia
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    *   Create a file named `.env` in the root directory.
    *   Add the necessary environment variables (refer to `database.py` and `main.py` for required keys like `SUPABASE_URL`, `SUPABASE_KEY`, `GOOGLE_API_KEY`).
    *   Example `.env` structure:
        ```dotenv
        SUPABASE_URL=your_supabase_url
        SUPABASE_KEY=your_supabase_anon_key
        GOOGLE_API_KEY=your_google_api_key
        # Add any other required variables
        ```
5.  **Run database migrations (if applicable):**
    *   Check scripts like `run_migrations.py` or SQL files in the `migrations` folder for setup steps.
    *   You might need to execute:
        ```bash
        python run_migrations.py
        ```
6.  **Run the application:**
    ```bash
    python main.py
    ```
7.  Access the application at `http://localhost:5000` (or the configured port).

## Usage Guide

1.  **Register/Login:** Create an account or log in as a patient or doctor.
2.  **Diagnosis:** Navigate to the diagnosis section, select your symptoms, and submit for a prediction.
3.  **Request Review:** After receiving a diagnosis, you can select an available, verified doctor to review your case.
4.  **History:** View your past diagnoses and their status in the history section.
5.  **Doctor Dashboard:** Doctors can log in to view assigned cases, review details, and provide feedback.
6.  **Admin Dashboard:** Admins can log in to verify new doctor registrations.
