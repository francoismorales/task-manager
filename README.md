# Task Manager — Gestor de tareas por equipo


## 🛠️ Stack tecnológico

### Backend
- **Python 3.11+** con **FastAPI** (validación automática con Pydantic, OpenAPI gratuito)
- **SQLAlchemy 2** (ORM) + **Alembic** (migraciones)
- **PostgreSQL** en producción · **SQLite** en local (cero setup)
- **JWT** (`python-jose`) + **bcrypt** para hashing de passwords
- **pytest** + **httpx** para tests

### Frontend
- **React 18** + **TypeScript**
- **Vite** como build tool
- **TailwindCSS** para estilos
- **React Router** para routing
- **Axios** con interceptores para auth

---

## 📐 Arquitectura

El backend usa **arquitectura por capas** (no MVC clásico) para respetar mejor SOLID:

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

**Por qué no MVC clásico:** los modelos en MVC mezclan persistencia y lógica.
Aquí cada cosa tiene su lugar. Los `routers` son "controllers" delgados;
los `services` orquestan reglas de negocio sin conocer HTTP; los `repositories`
encapsulan SQL. Esto cumple SRP, OCP y DIP.

**Excepciones de dominio:** los services lanzan `NotFoundError`,
`PermissionDeniedError`, `ConflictError`, `ValidationError`. Un único punto
en `core/error_handlers.py` las traduce a respuestas HTTP con el código
correcto.

### Modelo de datos

4 tablas relacionadas: `users`, `projects`, `project_members` (puente), `tasks`.
Índices en columnas de búsqueda. FKs con cascadas adecuadas (`CASCADE` para
hijos del proyecto, `SET NULL` para `assignee_id` cuando se borra un usuario).

---

## 🚀 Cómo correr el proyecto en local

### Prerrequisitos
- Python 3.11+
- Node.js 18+

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate            # Linux / macOS
venv\Scripts\Activate.ps1           # Windows PowerShell

pip install -r requirements.txt
cp .env.example .env

alembic upgrade head
python -m app.seed                  # opcional: datos de ejemplo

uvicorn app.main:app --reload
```

API en `http://localhost:8000`. Docs en `/docs`.

### 2. Frontend (otra terminal)

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend en `http://localhost:5173`.

### 3. Credenciales de ejemplo

Cualquiera con password `password123`:
- `alice@example.com` (owner del proyecto del seed)
- `bob@example.com` / `carol@example.com` (miembros)

---

## 🧪 Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v
```

11 tests que cubren el flujo de auth y la protección de endpoints.

---

## 🌍 Variables de entorno

### Backend (`backend/.env`)

| Variable | Descripción | Default |
|---|---|---|
| `DEBUG` | Modo debug. **En producción debe ser `False`** | `True` |
| `DATABASE_URL` | URL de la DB. Soporta `sqlite://`, `postgresql://`, `postgres://` | `sqlite:///./taskmanager.db` |
| `SECRET_KEY` | Clave JWT. **Obligatorio cambiar en producción** | placeholder |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Vida del token | `1440` (24h) |
| `CORS_ORIGINS` | Orígenes permitidos (CSV o JSON) | `localhost:5173, localhost:3000` |

> 🔒 La aplicación se **niega a arrancar** si `DEBUG=False` y `SECRET_KEY` sigue siendo el default. Genera uno con `openssl rand -hex 32`.

### Frontend (`frontend/.env`)

| Variable | Descripción |
|---|---|
| `VITE_API_URL` | URL del backend |

---

## 🚢 Despliegue

### Backend → Render

1. Push del repo a GitHub
2. En Render: **New +** → **Blueprint** → conectar el repo (lee `render.yaml`)
3. Setear `CORS_ORIGINS` en el dashboard con la URL del frontend
4. El primer deploy aplica migraciones automáticamente vía `start.sh`

`SECRET_KEY` lo genera Render con `generateValue: true`.

### Frontend → Vercel

1. **Import Project** → Root Directory: `frontend`
2. Variable de entorno: `VITE_API_URL` = URL del backend + `/api/v1`
3. Deploy. El `vercel.json` configura SPA routing.

Después actualiza `CORS_ORIGINS` en Render con la URL final de Vercel.

---
