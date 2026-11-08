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
* All dependency versions are pinned in the `requirements*.txt` files.

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

* **Git**
* **Docker Desktop**, running (for the recommended way), **or** **Python 3.11** (to run without Docker)
* A **Groq API key**: create one for free at [console.groq.com](https://console.groq.com) → API Keys

## 🔧 Setup (once)

1. Clone the repository and enter the folder:
   ```bash
   git clone https://github.com/DanaGazit/smart-student-exchange.git
   cd smart-student-exchange
   ```

2. Create your `.env` file from the template:
   ```bash
   cp .env.example .env
   ```

3. Open `.env` and set:
   * `GROQ_API_KEY`: your Groq API key
   * `SECRET_KEY`: a long random string, used to sign login tokens. To generate one:
     ```bash
     python3 -c "import secrets; print(secrets.token_hex(32))"
     ```

   The server will not start without `SECRET_KEY`. All other settings have defaults (see the Configuration section below).

## ▶️ Option A: Run with Docker (recommended)

From the project root:

```bash
docker compose -f docker/docker-compose.yml up -d --build
```

* The **first build** downloads and installs all libraries, which can take several minutes on a slow connection. Later builds are fast, because Docker caches the installed libraries until a `requirements*.txt` file changes.
* `-d` runs the containers in the background, so the terminal returns when they are up.

Then open:

| | URL |
|---|---|
| **App (UI)** | http://localhost:8501 |
| **API docs (Swagger)** | http://localhost:8000/docs |

Useful commands (all from the project root):

```bash
# Check that both containers are running (docker-backend-1, docker-frontend-1)
docker compose -f docker/docker-compose.yml ps

# Follow the backend logs
docker compose -f docker/docker-compose.yml logs -f backend

# Stop and remove the containers (your data in materials.db and uploads/ is kept)
docker compose -f docker/docker-compose.yml down
```

**Development mode:** the project folder is mounted into the containers and the backend runs with `--reload`, so code changes are picked up on save without rebuilding. Rebuild (`up -d --build`) only after changing a `requirements*.txt` file or a Dockerfile.

## ▶️ Option B: Run without Docker

Requires Python 3.11 (the version used in the Docker images and tested with the pinned dependencies). Check with `python3.11 --version`; on macOS you can install it with `brew install python@3.11`. You need **two terminals**, both in the project root.

**Terminal 1: backend**

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-frontend.txt
uvicorn app.main:app --reload
```

The backend runs at http://localhost:8000. It must be started from the project root, so it finds `.env`, `materials.db` and `uploads/`.

**Terminal 2: frontend**

```bash
source .venv/bin/activate          # Windows: .venv\Scripts\activate
BACKEND_API_URL=http://localhost:8000 streamlit run frontend/app.py
```

The UI opens at http://localhost:8501.

`BACKEND_API_URL` is required here: by default the frontend looks for `http://backend:8000`, the backend's name inside Docker, which does not exist outside it. On Windows (PowerShell), set it first with `$env:BACKEND_API_URL="http://localhost:8000"`, then run `streamlit run frontend/app.py`.

## 🧪 Running the Tests

The integration tests send real HTTP requests to a running backend at `http://localhost:8000` (start it with Option A or B first).

```bash
pip install -r requirements-dev.txt
python tests/test_api.py
```

They check registration and login, creating a material, that another user gets **403** when trying to edit or delete it, and that the owner can edit and delete it. The test material is deleted at the end; the two test users stay in `materials.db`.

## ⚙️ Configuration

All settings are read in `app/core/config.py` from environment variables or the `.env` file:

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | | Signs the JWT login tokens |
| `GROQ_API_KEY` | For AI analysis | | Groq API key. Without it, uploading a file for analysis returns an error |
| `GROQ_MODEL` | No | `qwen/qwen3.8-27b` | Groq vision model (must accept images) |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | How long a login stays valid |
| `DB_FILE` | No | `materials.db` | SQLite database file |
| `UPLOAD_DIR` | No | `uploads` | Folder for uploaded files |
| `BACKEND_API_URL` | No (frontend) | `http://backend:8000` | Where the frontend sends API requests. Set to `http://localhost:8000` when running without Docker |

## 🩺 Troubleshooting

* **`port is already allocated`** when starting Docker: another container or process is using port 8000 or 8501. List containers with `docker ps` and stop the old ones with `docker stop <name>`.
* **`ValueError: SECRET_KEY is missing in .env file!`**: `.env` is missing or has no `SECRET_KEY`. See Setup above.
* **The UI shows a connection error:** the backend is not running, or (without Docker) `BACKEND_API_URL` was not set to `http://localhost:8000`.
* **AI analysis returns an error that the AI service is busy or unavailable:** check `GROQ_API_KEY`. An error with code `429` means the Groq rate limit was reached; wait a minute and try again, or check your limits in the Groq console.
* **The first Docker build seems stuck:** it is most likely still downloading libraries. Check progress with `docker buildx history ls`.

## 👩‍💻 Author
**Dana Gazit** B.Sc. Computer Science Student @ Ben-Gurion University
