# 🎓 Smart Student Exchange

A full-stack platform for sharing physical and digital study materials between students. Take a photo or upload a PDF of a summary, exam or formula sheet, and AI fills in the details for you.

## 🚀 Key Features

* **AI Metadata Extraction:** Upload an image or PDF, and a Groq-hosted vision model (Qwen 3.8, configurable via `GROQ_MODEL`) extracts the course name, topic, material type, year, semester, lecturer and format. The user reviews and confirms before saving.
* **Decoupled Architecture:** A stateless REST API (FastAPI) and a separate UI (Streamlit) that talks to it only over HTTP.
* **Authentication & Ownership:** JWT-based login with bcrypt-hashed passwords. Only the user who uploaded a material can edit or delete it, enforced on the server.
* **Library per Institution:** Search, filter by material type, download the scan, or request the physical copy through a prefilled Gmail draft.
* **Availability Tracking:** Mark a material as available for pickup, digital only, or borrowed until a specific date.

## 🛠️ Tech Stack

* **Backend:** Python 3.11, FastAPI, SQLite, PyMuPDF, Pillow, Groq API
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
docker/
  Dockerfile.backend
  Dockerfile.frontend
  docker-compose.yml
requirements.txt              # Backend dependencies
requirements-frontend.txt     # Frontend dependencies
requirements-dev.txt          # Test dependencies (backend + requests)
.env.example                  # Template for the .env file
```

Created at runtime (not in git): `materials.db` (the SQLite database) and `uploads/` (uploaded files, served at `/downloads/...`).

## ✅ Prerequisites

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* A Groq API key from [console.groq.com](https://console.groq.com)

## ▶️ Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/DanaGazit/smart-student-exchange.git
   cd smart-student-exchange
   ```

2. Create a `.env` file from the template, and set `GROQ_API_KEY` and `SECRET_KEY` (any long random string):
   ```bash
   cp .env.example .env
   ```

3. Build and start the containers:
   ```bash
   docker compose -f docker/docker-compose.yml up -d --build
   ```

4. Open the app:
   * UI: http://localhost:8501
   * API docs (Swagger): http://localhost:8000/docs

To stop the app:
```bash
docker compose -f docker/docker-compose.yml down
```

The project folder is mounted into the containers and the backend runs with `--reload`, so code changes apply without rebuilding. Rebuild only after changing a `requirements*.txt` file or a Dockerfile.

## 🧪 Running the Tests

The integration tests run against the backend at `http://localhost:8000`, so start the app first:

```bash
pip install -r requirements-dev.txt
python tests/test_api.py
```

## ⚙️ Configuration

Settings are read from `.env` in `app/core/config.py`:

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | | Signs the JWT login tokens |
| `GROQ_API_KEY` | Yes | | Groq API key for AI analysis |
| `GROQ_MODEL` | No | `qwen/qwen3.8-27b` | Groq vision model |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Login token lifetime |
| `DB_FILE` | No | `materials.db` | SQLite database file |
| `UPLOAD_DIR` | No | `uploads` | Folder for uploaded files |

## 👩‍💻 Author
**Dana Gazit** B.Sc. Computer Science Student @ Ben-Gurion University
