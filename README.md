# 🏥 AI-Powered Smart Healthcare & Appointment Platform

> **Full-Stack Portfolio Project** | FastAPI · React 18 · SQLAlchemy · JWT · AI Engine · Docker · CI/CD

[![CI/CD](https://img.shields.io/badge/CI/CD-GitHub%20Actions-blue?logo=github-actions)](/.github/workflows/ci-cd.yml)
[![Tests](https://img.shields.io/badge/Tests-60%2B%20Passing-brightgreen?logo=pytest)](backend/tests/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue?logo=react)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](docker-compose.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Project Overview

A **production-grade, full-stack healthcare SaaS platform** built in 20 development phases, demonstrating:

- **Backend engineering** — FastAPI, SQLAlchemy ORM, 17 database models, JWT RBAC
- **AI/ML engineering** — Custom recommendation engine, conversational AI, RAG pipeline
- **Frontend engineering** — React 18, Vite, Glassmorphism SaaS design, 17 pages
- **DevOps** — Docker multi-stage builds, Nginx reverse proxy, GitHub Actions CI/CD
- **Software quality** — 60+ automated tests, audit logging, RBAC enforcement

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Nginx (Port 80)                        │
│              Reverse proxy + static file serving              │
└────────────────┬────────────────┬────────────────────────────┘
                 │                │
        ┌────────▼──────┐  ┌──────▼──────────┐
        │  React Frontend│  │  FastAPI Backend │
        │  (Vite + React)│  │  (Port 8000)    │
        │  Glassmorphism │  │  17 API Modules  │
        └───────────────┘  └──────┬───────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │      SQLite / MySQL         │
                    │   17 Tables · ORM Models    │
                    └────────────────────────────┘
```

---

## ✨ Features by Phase

| # | Phase | Key Technology |
|---|-------|---------------|
| 1 | Project Structure + FastAPI + SQLAlchemy | FastAPI, SQLAlchemy ORM, 17 models |
| 2 | JWT Authentication + RBAC | python-jose, bcrypt, role guards |
| 3 | Patient & Doctor Profile Management | CRUD APIs, profile auto-creation |
| 4 | Department Management | Seeded hospital departments |
| 5 | Doctor Availability, Slots & Leave | 30-min slot generation, leave exclusion |
| 6 | Appointment Booking & Management | Full lifecycle, double-booking prevention |
| 7 | Smart Waitlist & Live Queue | Auto-notification, real-time queue status |
| 8 | React.js Frontend | React 18, Vite, Glassmorphism, 17 pages |
| 9 | AI Assistant & Care Navigation | Intent classification, safety guardrails |
| 10 | Doctor Matching Algorithm | 5-factor scoring, transparent reasons |
| 11 | Notification System | In-app real-time alerts, unread badges |
| 12 | Medical Document Upload & RAG | File validation, chunk pipeline |
| 13 | Analytics Dashboard | KPIs, revenue, trends, dept breakdown |
| 14 | Feedback & Doctor Rating | Live rating recalculation |
| 15 | Audit Logging & Security | Immutable API audit trail middleware |
| 16 | Docker Containerization | Multi-stage Dockerfile, docker-compose |
| 17 | CI/CD (GitHub Actions) | Tests → Build → Docker → Deploy gate |
| 18 | API Documentation Polish | OpenAPI, Swagger UI, rich descriptions |
| 19 | Integration Test Coverage | End-to-end cross-module tests |
| 20 | Final README & Portfolio | This document |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (optional)

### Option A — Local Development

```bash
# 1. Clone
git clone https://github.com/your-username/ai-healthcare-platform.git
cd ai-healthcare-platform

# 2. Backend
cd backend
python -m venv venv
.\venv\Scripts\activate          # Windows
# source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

**API Docs**: http://localhost:8000/docs  
**Frontend**: http://localhost:5173

### Option B — Docker Compose

```bash
docker-compose up --build
```

**App**: http://localhost | **API**: http://localhost/api/v1

---

## 🧪 Running Tests

```bash
cd backend
.\venv\Scripts\pytest.exe -v          # All 60+ tests
.\venv\Scripts\pytest.exe tests/test_integration.py -v   # Integration only
```

**Test Coverage by Module:**

| Module | Tests |
|--------|-------|
| Auth & RBAC | 5 |
| Patient/Doctor Profiles | 3 |
| Department Management | 3 |
| Availability & Slots | 2 |
| Appointment Lifecycle | 2 |
| Waitlist & Queue | 2 |
| AI Care Navigator | 4 |
| Doctor Recommendations | 6 |
| Notifications | 6 |
| Document Upload & RAG | 5 |
| Analytics Dashboard | 7 |
| Feedback & Ratings | 5 |
| Audit Logging | 3 |
| Integration Tests | 5+ |
| **Total** | **60+** |

---

## 📡 API Reference

Full interactive docs available at `/docs` (Swagger UI) and `/redoc` after starting the server.

### Key Endpoints

```
POST   /api/v1/auth/register          Register (PATIENT | DOCTOR | ADMIN)
POST   /api/v1/auth/login             Get JWT tokens
POST   /api/v1/ai/chat                AI Care Navigator chat
GET    /api/v1/recommendations/       Smart doctor matching
POST   /api/v1/appointments           Book appointment
GET    /api/v1/appointments           View schedule
POST   /api/v1/documents/upload       Upload medical document (PDF/PNG/DOCX)
GET    /api/v1/analytics/dashboard    Admin analytics (Admin only)
GET    /api/v1/audit                  Audit logs (Admin only)
POST   /api/v1/feedback               Submit doctor review
```

---

## 🗄️ Database Schema (17 Models)

```
users ──────────────── patients, doctors
departments ─────────── doctors
doctors ─────────────── doctor_availability, doctor_leave, appointments
appointments ────────── feedback, waitlists
conversations ───────── messages
documents ───────────── document_chunks_metadata
users ───────────────── notifications, audit_logs
```

---

## 🔐 Security Features

- **JWT Auth** — Short-lived access tokens (30 min) + long-lived refresh tokens (7 days)
- **RBAC** — Patient / Doctor / Admin role enforcement on every protected route
- **Audit Logging** — Every `POST/PUT/PATCH/DELETE` logged to `audit_logs` with user ID and IP
- **File Validation** — Extension + content-type + size (10 MB) checked before disk write
- **Password Hashing** — bcrypt with salt rounds
- **CORS** — Configurable allowed origins

---

## 🤖 AI Features

### Care Navigator
- Local intent classification (no external API required)
- Department routing by symptom keyword matching
- Safety disclaimer auto-triggered for diagnostic queries
- Conversation persistence with message history

### Doctor Recommendation Engine
- **5-factor scoring**: Specialty match (40%) + Availability (20%) + Rating (20%) + Experience (10%) + Fee (10%)
- Transparent `match_reasons` in every response
- Hard filters: max fee, minimum rating

### RAG Document Pipeline
- Upload → validate → save to per-user isolated storage
- Text chunking (500 chars) → `chroma_id` assignment → `document_chunks_metadata` table
- Production-ready: plug in ChromaDB/Pinecone to activate full vector search

---

## 🎨 Frontend (React 18)

| Page | Description |
|------|-------------|
| Landing | Hero + feature overview |
| Login / Register | JWT auth with role selection |
| Patient Dashboard | Appointment overview, notifications |
| Doctor Dashboard | Schedule, availability management |
| Admin Dashboard | Analytics, user management |
| AI Chat | Conversational care navigator |
| Book Appointment | Doctor search + slot selection |
| Documents | Upload and manage medical records |
| Notifications | Real-time in-app alert center |
| Feedback | Star rating + review form |
| Analytics | Charts and KPI cards (Admin) |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| FastAPI 0.111 | Async REST API framework |
| SQLAlchemy 2.0 | ORM with declarative models |
| Pydantic v2 | Request/response schema validation |
| python-jose | JWT token creation and verification |
| bcrypt | Password hashing |
| SQLite (dev) / MySQL (prod) | Database |
| Uvicorn | ASGI server |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 18 | UI framework |
| Vite | Build tool + dev server |
| Axios | HTTP client with JWT interceptors |
| React Router v6 | Client-side routing |
| Tailwind CSS | Utility-first styling |

### DevOps
| Technology | Purpose |
|-----------|---------|
| Docker + Docker Compose | Containerized deployment |
| Nginx | Reverse proxy + static serving |
| GitHub Actions | CI/CD pipeline |
| pytest | Backend test runner |

---

## 👨‍💻 About This Project

Built as a **portfolio-grade** project to demonstrate full-stack engineering depth across:

- System design with 20 phased deliverables
- Backend architecture (service layer pattern, dependency injection, ORM)
- AI/ML engineering (scoring engines, NLP classification, RAG)
- Frontend SaaS UX (Glassmorphism design, JWT interceptors, state management)
- DevOps (Docker, Nginx, GitHub Actions CI/CD)
- Software quality (60+ tests, audit logging, RBAC)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
