# Task Manager — Gestor de tareas por equipo

---
## 🔗 Demo desplegada

- **App (frontend)**: https://task-manager-ruddy-sigma.vercel.app
- **API (backend)**: https://taskmanager-api-310h.onrender.com
- **Docs interactivas (Swagger)**: https://taskmanager-api-310h.onrender.com/docs

### ⚠️ Nota importante: despertar el backend antes de usar la app

El backend está alojado en **Render free tier**, que duerme el servicio tras 15 minutos sin tráfico para ahorrar recursos. La primera petición tarda **30–50 segundos** en despertarlo (las siguientes son instantáneas).

## 🚀 Cómo correr el proyecto en local

### Prerrequisitos
- Python 3.11+
- Node.js 18+

### 1. Backend

```bash
cd backend

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate            # Linux / macOS
venv\Scripts\Activate.ps1           # Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Aplicar migraciones (crea la DB SQLite local)
alembic upgrade head

# (Opcional) Poblar con datos de ejemplo
python -m app.seed

# Levantar el servidor
uvicorn app.main:app --reload
```

API en `http://localhost:8000`. Docs interactivas en `/docs`.

### 2. Frontend (otra terminal)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App en `http://localhost:5173`.

### 3. Credenciales de ejemplo (si corriste el seed)

Cualquiera con password `password123`:
- `alice@example.com` (owner del proyecto del seed)
- `bob@example.com` / `carol@example.com` (miembros)

### 4. Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

22 tests cubriendo auth, protección de endpoints, gestión de miembros y cascadas.

---

## 🛠️ Stack tecnológico

**Backend:** Python 3.11+ · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL (prod) / SQLite (local) · JWT + bcrypt · pytest

**Frontend:** React 18 · TypeScript · Vite · TailwindCSS · React Router · Axios

---

## 📐 Arquitectura

El backend usa **arquitectura por capas**:

```
backend/app/
├── core/           # config, db, security, exception handlers
├── models/         # entidades SQLAlchemy
├── schemas/        # DTOs Pydantic (validación de request/response)
├── repositories/   # acceso a datos — única capa que toca la DB
├── services/       # lógica de negocio + autorización
├── routers/        # endpoints HTTP (capa thin que delega en services)
├── dependencies/   # inyección de dependencias de FastAPI
└── main.py         # application factory
```

### Modelo de datos

4 tablas relacionadas: `users`, `projects`, `project_members` (puente), `tasks`. Índices en columnas de búsqueda. FKs con cascadas adecuadas (`CASCADE` para hijos del proyecto, `SET NULL` para `assignee_id` cuando se borra un usuario).

