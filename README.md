# 🎓 Smart Student Exchange

A next-generation, AI-powered platform designed to help university students share, borrow, and exchange physical and digital study materials.

**"Pay it Forward!"** - Got printed summaries lying around at home? Spent hours on a summary or formula sheet? Pay it forward! Instead of throwing them away at the end of the semester, this system allows you to easily pass them on to students who need them right now.

## ✨ Key Features
* **AI-Powered OCR & Categorization:** Upload a photo or PDF of a study material. The system uses Google's Gemini AI to automatically extract the course name, topic, semester, and material format.
* **Smart Filtering & Search:** A dynamic library that allows students to search by free text or filter by specific material types available in real-time.
* **Physical & Digital Exchange:** Download digital files directly, or use the one-click Gmail integration to coordinate physical handoffs for notebooks and printed materials.
* **Frictionless Experience:** Clean, responsive UI built with modern principles, requiring zero manual typing for material categorization.

## 🛠️ Tech Stack & Architecture
* **Frontend:** Streamlit (Python) - For a fast, interactive, and responsive UI.
* **Backend:** FastAPI (Python) - Providing robust RESTful API endpoints.
* **Database:** SQLite - Embedded local database for metadata storage.
* **AI Integration:** Google GenAI SDK (Gemini 2.5 Flash) for image-to-text and structural JSON extraction.
* **DevOps:** Docker & Docker Compose - Containerized for seamless local development and easy deployment.

## 🚀 How to Run Locally (For Reviewers & Developers)

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/danagazit02-wq/smart-student-exchange.git](https://github.com/danagazit02-wq/smart-student-exchange.git)
   cd smart-student-exchange
   ```

2. **Set up environment variables:**
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Run with Docker:**
   Make sure Docker Desktop is running, then execute:
   ```bash
   docker-compose up -d --build
   ```

4. **Access the Application:**
   * Frontend (UI): http://localhost:8501
   * Backend API Docs (Swagger): http://localhost:8000/docs

## 👩‍💻 Author
**Dana Gazit** B.Sc. Computer Science Student @ Ben-Gurion University