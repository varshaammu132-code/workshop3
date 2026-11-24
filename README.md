# 🎓 EduTrack - Student Management System

A simple, beginner-friendly, and modern full-stack **Student Management System** web application. Built using **Python FastAPI**, **SQLite**, and vanilla **HTML, CSS, and JavaScript**.

---

## 🌟 Features

1. **Dashboard Metrics**: Live statistics displaying Total Students, Department distribution, Semesters, and System connectivity.
2. **Add New Students**: User-friendly modal form with real-time validation (USN, Full Name, Email, Phone, Department, Semester, Gender).
3. **View & Search**:
   - Dynamic tabular view with colored avatars and badges.
   - Real-time search by **Student Name** or **USN**.
   - Filter by **Department** (Computer Science, Information Science, Electronics, AI & ML, Mechanical, Civil, etc.).
   - Filter by **Semester** (Semesters 1 through 8).
4. **Update Student Details**: In-place edit modal allowing updates to student contact info, department, semester, and USN (with conflict detection).
5. **Delete Records**: Safe deletion with confirmation modal to prevent accidental data loss.
6. **Auto-Seeding**: Comes pre-populated with initial sample student records on first startup.
7. **Interactive API Documentation**: Full Swagger UI (`/docs`) and ReDoc (`/redoc`) powered by FastAPI.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, CSS3, Modern JavaScript (ES6+) | Responsive UI with vibrant gradients, modals, toasts, and real-time search |
| **Backend** | Python 3.12+, FastAPI | High-performance asynchronous REST API framework |
| **ASGI Server** | Uvicorn | Lightning-fast ASGI web server |
| **Database** | SQLite + SQLAlchemy 2.0 | Lightweight file-based relational database with ORM |
| **Data Validation** | Pydantic v2 | Robust schema validation and error responses |
| **API Testing** | Swagger UI (`/docs`) & unittest | Interactive browser-based API testing & automated test suite |

---

## 📁 Project Folder Structure

```text
student-management-system/
├── backend/
│   ├── app/
│   │   ├── __init__.py         # Package initialization
│   │   ├── database.py         # SQLite connection & SQLAlchemy session management
│   │   ├── models.py           # Student database model definition
│   │   ├── schemas.py          # Pydantic schemas for request/response validation
│   │   ├── crud.py             # Database CRUD helper functions & sample data seeder
│   │   └── main.py             # FastAPI REST endpoints & static file serving
│   ├── requirements.txt        # Backend dependencies list
│   └── students.db             # SQLite database file (created automatically on run)
├── frontend/
│   ├── index.html              # Main single-page application dashboard
│   ├── css/
│   │   └── style.css           # Modern styles, color scheme, responsive layout
│   └── js/
│       └── app.js              # REST API client, table rendering, modals, and search
├── run.py                      # One-click launcher (runs Uvicorn and opens browser)
├── start.bat                   # Windows batch file for double-click startup
├── test_api.py                 # Automated unit and integration test suite
├── requirements.txt            # Root dependencies list
└── README.md                   # Project documentation & setup instructions
```

---

## 🚀 Setup & Execution Instructions (Windows)

### Prerequisites
- Windows 10/11 laptop
- Python 3.10, 3.11, or 3.12 installed
- Visual Studio Code (optional, but recommended)

### Step 1: Open the Project in VS Code
1. Open Visual Studio Code.
2. Click **File** > **Open Folder...**
3. Navigate to:
   ```text
   C:\Users\Admin\.gemini\antigravity\scratch\student-management-system
   ```
4. Click **Select Folder**.

### Step 2: Open VS Code Integrated Terminal
- Press `Ctrl + ~` (or select **Terminal** > **New Terminal** in the top menu).

### Step 3: Install Required Dependencies
Run the following command in the terminal:
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
You can run the application in any of the following ways:

#### Option A: Run the launcher (Recommended)
```powershell
python run.py
```
*This starts the server and automatically opens your default web browser to `http://127.0.0.1:8000`.*

#### Option B: Run directly with Uvicorn
```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```
Then open your browser and navigate to `http://127.0.0.1:8000`.

#### Option C: Windows Double-Click
- In Windows File Explorer, double-click `start.bat`.

---

## 🌐 Application URLs

- **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 REST API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the frontend single-page application |
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/stats` | Dashboard aggregate statistics (total count, department breakdown) |
| `GET` | `/api/students` | Get all students (supports `?search=`, `?department=`, `?semester=`) |
| `GET` | `/api/students/{id}` | Get student details by ID |
| `POST` | `/api/students` | Create/register a new student (validates unique USN) |
| `PUT` | `/api/students/{id}` | Update student details |
| `DELETE` | `/api/students/{id}` | Delete a student record |

---

## 🧪 Running Automated Tests

Run the included integration test suite to verify all endpoints and database operations:

```powershell
python test_api.py
```

Expected output:
```text
.........
----------------------------------------------------------------------
Ran 9 tests in 0.151s

OK
```

---

## 📝 Code Explanation for Beginners

1. **`database.py`**:
   - Creates the connection to `students.db` via SQLAlchemy.
   - Provides `get_db()` which gives each request a fresh database session and safely closes it when finished.

2. **`models.py`**:
   - Defines the database schema for the `students` table.
   - Declares columns like `usn`, `name`, `email`, `phone`, `department`, `semester`, and `gender`.

3. **`schemas.py`**:
   - Defines Pydantic data models for incoming HTTP request data and outgoing API responses.
   - Validates that email formats are correct, USN is in uppercase, phone contains digits, and semester is within 1 to 8.

4. **`crud.py`**:
   - Contains clean Python functions for Create, Read, Update, and Delete operations using SQLAlchemy queries.
   - Includes automatic seeding so you don't start with a blank database!

5. **`main.py`**:
   - Defines the FastAPI app, sets up Cross-Origin Resource Sharing (CORS), wires up route endpoints, and mounts the frontend HTML, CSS, and JS static files.

6. **`app.js`**:
   - Uses the modern browser `fetch()` API to send asynchronous requests to FastAPI.
   - Dynamically creates table rows, handles instant filtering with debounce, and triggers modals and toast notifications.
