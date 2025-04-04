# Task Management - Gestor de Tareas con Django, Django Restframework y Docker

## Descripción del Proyecto

Task Management es un servicio web para la gestión de tareas inspirada en Trello, que permite a los usuarios organizar y dar seguimiento a sus actividades de manera eficiente. El sistema está diseñado para equipos que necesitan una herramienta sencilla para gestionar su flujo de trabajo.

### Características Principales

- Gestión completa del ciclo de vida de tareas
- Sistema de prioridades
- Seguimiento de fechas de  asignacion de la tarea.
- Asignación de usuarios a tareas
- Historial de comentarios para cada tarea.
- Interfaz para cambios de estado de la tarea.

## Flujo de Trabajo

El flujo de trabajo en Task Management sigue un proceso Kanban simplificado:

1. Las tareas se crean inicialmente en estado **BACKLOG**
2. Cuando se decide trabajar en una tarea, se modifica a **TO DO**
3. Al iniciar el trabajo activo, la tarea se modifica a **DOING**
4. Una vez completada, la tarea se modifica a **TEST** para verificación
5. Finalmente, las tareas verificadas se marcan como **DONE**

En cualquier momento del proceso, se pueden actualizar los detalles de la tarea, ajustar su prioridad, cambiar la fecha de entrega o añadir comentarios para documentar el progreso.

## Arquitectura del Proyecto

Task Management utiliza una arquitectura de microservicios containerizada, con los siguientes componentes principales:

```
┌───────────────┐      ┌────────────────┐     ┌─────────────────┐
│               │      │                │     │                 │
│  Cliente Web  │────▶│  API Backend   │────▶│  Base de Datos  │
│  (Navegador)  │◀────│  (Django REST) │◀────│  (PostgreSQL)   │
│               │      │               │      │                 │           │
└───────────────┘      └───────────────┘      └─────────────────┘
```

### Componentes

- **Backend**: API RESTful desarrollada con Django Rest Framework que maneja la lógica de negocio
- **Base de datos**: PostgreSQL para almacenamiento persistente de datos
- **Contenedores**: Docker y Docker Compose para la gestión y orquestación de servicios

### Diagrama de Arquitectura Detallado

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                     Docker Compose                                     │
│                                                                                        │
│                      ┌─────────────┐              ┌──────────────┐                     │
│                      │             │              │              │                     │
│                      │  Backend    │              │  Database    │                     │
│                      │  Container  │              │  Container   │                     │
│                      │  (Django)   │              │  (PostgreSQL)│                     │
│                      │             │              │              │                     │
│                      └──────┬──────┘              └───────┬──────┘                     │
│                             │                             │                            │
└────────────────┼────────────┼─────────┼───────────────────┼────────────────────────────┘
                              │                             │
                              ▼                             ▼
                       ┌─────────────┐              ┌─────────────┐
                       │             │              │             │
                       │  Aplicación │              │ Volumen de  │
                       │  Django     │              │ datos       │
                       │             │              │ persistentes│
                       │             │              │             │
                       └─────────────┘              └─────────────┘
```

## Estructura del Proyecto

```
gestion_tareas/
├── app_tareas/                # Aplicación de tareas tareas.
│   ├── __pycache__/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py               # Configuración del panel de administración.
│   ├── apps.py                # Configuración de la aplicación.
│   ├── models.py              # Modelos de datos del proyecto.
│   ├── serializers.py         # Serializadores para la API.
│   ├── signals.py             # Señales de Django.
│   ├── tests.py               # Pruebas unitarias.
│   ├── urls.py                # URLs de la API.
│   └── views.py               # Vistas de la API.
├── gestion_tareas/            # Configuración del proyecto.
│   ├── __pycache__/
│   ├── __init__.py
│   ├── asgi.py                # Configuración ASGI.
│   ├── settings.py            # Configuraciones del proyecto.
│   ├── urls.py                # URLs del proyecto.
│   └── wsgi.py                # Configuración WSGI.
├── .env                       # Variables de entorno.
├── .env_example               # Ejemplo de variables de entorno.
├── docker-compose.yml         # Configuración de Docker Compose.
├── dockerfile                 # Configuración de Docker.
├── manage.py                  # Script de administración de Django.
├── requirements.txt           # Dependencias.
├── .gitignore                 # Configuración de Git.
└── README.md                  # Este archivo.
```

## Configuración y Ejecución

### Requisitos Previos

- Docker y Docker Compose, Python, Django, Django REST Framework y Postman instalados en su sistema.
- Git para clonar el repositorio.


### Pasos para Ejecutar el Proyecto

1. Clonar el repositorio:
```bash
git clone https://github.com/fabiiann1/Management-Tasks.git
cd Management-Task
cd gestion_tareas
code . #Abre el proyecto en vs code.
```

2. Crear archivo de variables de entorno:
```bash
# Editar el archivo .env con los valores adecuados
```

3. Ejecutar el comando de shell de bash:
```bash
docker-compose exec web bash
```

3. Ejecutar migraciones:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Crear superusuario (opcional):
```bash
python manage.py createsuperuser
```

5. Construir y levantar los contenedores:
```bash
docker-compose build
docker-compose up
```

7. Acceder a la aplicación:
   - API Backend: http://localhost:8000/api/register/
   - Interfaz de administración: http://localhost:8000/admin/



### Comandos Útiles

```bash
# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Ejecutar pruebas
python manage.py test
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `http://localhost:8000/api/tasks/` | Obtiene la lista de todas las tareas |
| POST | `http://localhost:8000/api/register/` | Registra un nuevo usuario |
| POST | `http://localhost:8000/api/tasks/` | Crea una nueva tarea |
| GET | `http://localhost:8000/api/tasks/{id}/` | Obtiene detalles de una tarea específica |
| PUT | `http://localhost:8000/api/tasks/{id}/` | Actualiza una tarea completa |
| PATCH | `http://localhost:8000/api/tasks/{id}/` | Actualiza parcialmente una tarea |
| DELETE | `http://localhost:8000/api/tasks/{id}/` | Elimina una tarea |
| GET | `http://localhost:8000/api/tasks/?state={status}` | Filtra tareas por estado |
| GET | `http://localhost:8000/api/tasks/?due_date={due_date}` | Filtra tareas por fecha de entrega |
| GET | `http://localhost:8000/api/tasks/?assigned_user__username={user_name}` | Filtra tareas por nombre de usuario |.

## Contacto

- Desarrollador: Fabian Alexis Marín Manciple, Ivan Alejandro Cosme.
- Email: practicantesena@ticsocial.com.co, practicantesena9@ticsocial.com.co.
- Repositorio: https://github.com/fabiiann1, https://github.com/IVAN-LAMUTE. 