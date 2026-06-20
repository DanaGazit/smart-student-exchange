# 🎓 Smart Student Exchange

A fully containerized full-stack platform designed to facilitate the sharing and exchanging of physical and digital academic study materials among students.

## 🚀 Key Features

* **AI-Powered OCR & Metadata Extraction:** Upload a picture or PDF of a study document, and the integrated Groq AI (Llama 4 Vision) automatically extracts relevant metadata (Course Name, Topic, Semester, Document Type).
* **Decoupled Architecture:** Built with a stateless, RESTful FastAPI backend and a clean Streamlit frontend UI.
* **Robust Security:** Implements JWT-based authentication with Owner-based Access Control. Users can only edit or delete materials they personally uploaded.
* **Dynamic Availability Tracking:** Real-time tracking of material status (e.g., physical delivery, digital-only, or borrowed with dynamic return dates).
* **Database Deadlock Prevention:** Engineered with safe SQLite connection handling to ensure robust concurrency during heavy read/write operations.

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, SQLite, PyMuPDF, Groq API
* **Frontend:** Streamlit, Requests
* **Infrastructure:** Docker, Docker Compose

## ⚙️ How to Run Locally

1. Clone this repository.

2. Create a `.env` file in the root directory (use `.env.example` as a template) and insert your Groq API key.

3. Start the application using Docker:
   ```bash
   docker-compose up -d --build

4. **Access the Application:**
   * Frontend (UI): http://localhost:8501
   * Backend API Docs (Swagger): http://localhost:8000/docs

## 👩‍💻 Author
**Dana Gazit** B.Sc. Computer Science Student @ Ben-Gurion University