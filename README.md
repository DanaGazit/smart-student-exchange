# 🎓 Smart Student Exchange

A fully containerized full-stack platform designed to facilitate the sharing and exchanging of physical and digital academic study materials among students.

## 🚀 Key Features

* **AI-Powered OCR & Metadata Extraction:** Upload a picture or PDF of a study document, and the integrated Groq AI (Qwen 3.8 vision model, configurable via `GROQ_MODEL`) automatically extracts relevant metadata (Course Name, Topic, Semester, Document Type).
* **Decoupled Architecture:** Built with a stateless, RESTful FastAPI backend and a clean Streamlit frontend UI.
* **Robust Security:** Implements JWT-based authentication with Owner-based Access Control. Users can only edit or delete materials they personally uploaded.
* **Dynamic Availability Tracking:** Real-time tracking of material status (e.g., physical delivery, digital-only, or borrowed with dynamic return dates).
* **Database Deadlock Prevention:** Engineered with safe SQLite connection handling to ensure robust concurrency during heavy read/write operations.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, SQLite, PyMuPDF, Groq API
* **Frontend:** Streamlit, Requests
* **Infrastructure:** Docker, Docker Compose

## 🗂️ Project Structure

The backend is split into layers, each with a single responsibility:

```
app/                          # Backend (FastAPI)
  main.py                     #   App setup: creates FastAPI, connects the routers
  schemas.py                  #   Pydantic request models
  core/                       #   Cross-cutting infrastructure
    config.py                 #     All environment variables, read in one place
    security.py               #     Password hashing (bcrypt) and JWT creation
    database.py               #     SQLite connection and table creation
  api/                        #   HTTP layer
    dependencies.py           #     get_current_user: JWT validation for protected endpoints
    routers/                  #     Endpoints, request in -> response out
      auth_router.py          #       /register, /login
      materials_router.py     #       /materials, /analyze-material
  services/                   #   Business logic
    auth_service.py           #     registration and login
    materials_service.py      #     ownership checks, file upload handling
    ai_service.py             #     PDF/image processing and the Groq AI call
  repositories/               #   Data access: SQL queries only
    users_repository.py
    materials_repository.py
frontend/
  app.py                      # Streamlit UI
tests/
  test_api.py                 # Integration tests (run against a running backend)
docker/                       # Dockerfiles and docker-compose.yml
requirements.txt              # Backend dependencies
requirements-frontend.txt     # Frontend dependencies
requirements-dev.txt          # Dev / test dependencies
```

## ⚙️ How to Run Locally

1. Clone this repository.

2. Create a `.env` file in the root directory (use `.env.example` as a template) and insert your Groq API key and a `SECRET_KEY`.

3. Start the application using Docker:
   ```bash
   docker compose -f docker/docker-compose.yml up -d --build
   ```

   Or run the backend without Docker (from the project root):
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

   Run the integration tests against a running backend:
   ```bash
   pip install -r requirements-dev.txt
   python tests/test_api.py
   ```

4. **Access the Application:**
   * Frontend (UI): http://localhost:8501
   * Backend API Docs (Swagger): http://localhost:8000/docs

## 👩‍💻 Author
**Dana Gazit** B.Sc. Computer Science Student @ Ben-Gurion University