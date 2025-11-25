# Gestión de Furgones - Proyecto Django

Este repositorio contiene el esqueleto inicial de un proyecto Django para gestionar furgones escolares, modelado según los diagramas UML provistos.

Requisitos:
- Python 3.10+ (recomendado)

Instrucciones rápidas (Windows PowerShell):

1. Crear y activar entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Migrar la base de datos:

```powershell
python manage.py migrate
```

4. Crear superusuario (opcional):

```powershell
python manage.py createsuperuser
```

5. Ejecutar servidor de desarrollo:

```powershell
python manage.py runserver
```

Panel administrativo: `http://127.0.0.1:8000/admin/`

Siguientes pasos sugeridos:
- Implementar API REST (con Django REST Framework ya incluido)
- Añadir autenticación y permisos
- Añadir pruebas unitarias y de integración
- Configurar despliegue (Heroku, Docker, o proveedor cloud)

Pre-commit, linting y formateo
 - Este repositorio incluye configuración para `pre-commit` (`.pre-commit-config.yaml`) con `black`, `isort` y `flake8`.
 - Para activar localmente:

```powershell
pip install -r requirements.txt
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Postman y ejemplos
 - Importa `postman_collection.json` y `postman_environment.json` en Postman. Ajusta `username`/`password` si lo deseas.

CI (GitHub Actions)
 - El workflow en `.github/workflows/ci.yml` ejecuta linters y tests con coverage en pushes y PRs a `main`.

Badges (activables al pushear a GitHub):

- CI: [![CI](https://github.com/DaniznX/Gestion_de_Furgones/actions/workflows/ci.yml/badge.svg)](https://github.com/DaniznX/Gestion_de_Furgones/actions)
- Coverage: [![Coverage](https://img.shields.io/codecov/c/github/DaniznX/Gestion_de_Furgones?logo=codecov&style=flat-square)](https://codecov.io/gh/DaniznX/Gestion_de_Furgones)

Coverage & badge notes
- Las acciones de CI ahora generan un reporte de cobertura (XML) y lo suben a Codecov; cuando pushes al repo GitHub, la badge de coverage se actualizará.
- Si el repositorio es privado, quizá necesites configurar el token de Codecov como secreto `CODECOV_TOKEN` en los settings del repo en GitHub.

Frontend (server-side)
- Se añadió una app `frontend` con vistas y plantillas (Django templates + Bootstrap CDN) para manejar CRUD y acciones:
	- Rutas principales: `/` (dashboard), `/login/` y `/logout/`.
	- Recursos: `/colegios/`, `/conductores/`, `/furgones/`, `/estudiantes/`, `/rutas/`, `/notificaciones/`, `/pagos/`, `/asistencias/`.
	- Acciones especiales: desde la lista de furgones puedes enviar lat/lon para `update_location`; en notificaciones puedes marcar como leída.

Uso de la UI localmente
1. Inicia el servidor local:

```powershell
python manage.py runserver
```

2. Abre `http://127.0.0.1:8000/` y haz login con el superusuario creado por `manage.py seed` (usuario `admin` / contraseña `adminpass` por defecto si usaste el seed).

3. Navega por las secciones del menú para crear/editar y utilizar las funciones del sistema.


