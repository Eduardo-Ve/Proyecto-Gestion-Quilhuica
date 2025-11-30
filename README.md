# Proyecto – Sistema de Gestión Quilhuica

Aplicación web desarrollada con Django para la gestión eficiente de inventarios, bodegas, usuarios y operaciones internas.  
Diseñada para ser moderna, escalable y segura.

---

## Tecnologías Utilizadas

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)]()
[![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)]()
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)]()
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)]()
[![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white)]()
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)]()
[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)]()

---

## Tabla de Contenidos

- [Acerca del Proyecto](#acerca-del-proyecto)
- [Tecnologías Usadas](#tecnologías-usadas)
- [Características del Sistema](#características-del-sistema)
- [Instalación](#instalación)
- [Configuración del Entorno](#configuración-del-entorno)
- [Ejecución del Proyecto](#ejecución-del-proyecto)
- [Contribución](#contribución)

---

## Acerca del Proyecto

El Sistema de Gestión Quilhuica es una plataforma web para administrar inventarios, bodegas, movimientos de productos y usuarios dentro de una organización.  
Incluye autenticación personalizada, reportes automáticos, paneles administrativos y un flujo optimizado para el manejo de operaciones.

Este proyecto está pensado para ambientes reales en producción y soporta tanto PostgreSQL como SQLite para desarrollo local.

---

## Tecnologías Usadas

- Python 3.11+
- Django 4.2+
- HTML5 y CSS3
- Bootstrap 5
- JavaScript Vanilla
- PostgreSQL o SQLite
- Git y GitHub Actions

---

## Características del Sistema

- Autenticación y roles personalizados  
- Control de inventario por producto  
- Gestión de bodegas y trazabilidad  
- Registro de movimientos (entradas, salidas, traslados)  
- Panel administrativo y dashboards  
- Sistema de notificaciones  
- Interfaz responsiva  
- Arquitectura modular  
- Soporte PWA 
- Reportes automáticos  

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Eduardo-Ve/Proyecto-Gestion-Quilhuica
cd Proyecto-Gestion-Quilhuica/inventario-quilhuica/gestion

2. Instalar dependencias
pip install -r requirements.txt

3. Migrar la base de datos
python manage.py migrate

Configuración del Entorno

Crear un archivo .env en la raíz del proyecto con los siguientes valores:

DEBUG=True
SECRET_KEY=tu_clave_segura
ALLOWED_HOSTS=127.0.0.1,localhost
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

Para PostgreSQL:

DB_ENGINE=django.db.backends.postgresql
DB_NAME=quilhuica
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

Ejecución del Proyecto
python manage.py runserver


Abrir en el navegador:
http://127.0.0.1:8000/
```

## Contribución

Las contribuciones son bienvenidas.
Para proponer cambios:

```

  git checkout -b feature/nueva-funcionalidad
  git commit -m "Agrega nueva funcionalidad"
  git push origin feature/nueva-funcionalidad

```

Se aceptan mejoras en:

* Funcionalidades
* Correcciones de bugs
* Documentación
* Interfaz y experiencia de usuario

