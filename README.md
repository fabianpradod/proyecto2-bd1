# Atelier Formal

Aplicacion web para gestionar inventario, ventas y reportes de una tienda de ropa formal.

## Requisitos

- Docker y Docker Compose.
- Credenciales fijas de base de datos: usuario `proy2`, contrasena `secret`.

## Levantar desde cero

```bash
cp .env.example .env
docker compose up --build
```

Servicios:

- Frontend: http://localhost:8080
- Backend: http://localhost:8000
- Healthcheck: http://localhost:8000/api/health
- PostgreSQL local: `localhost:55432`

Si se necesita recrear la base de datos con los scripts iniciales:

```bash
docker compose down -v
docker compose up --build
```

## Funcionalidades

- Gestion completa de productos.
- Gestion completa de categorias.
- Registro de ventas con control de stock.
- Validacion visible de errores de API en la interfaz.
- Reportes de ventas, categorias, productos destacados, reposicion y productos sin ventas.
- Exportacion CSV del reporte de categorias.

## Estructura

- `proyecto2-bd1-db/ddl.sql`: esquema, llaves, checks, indices y vista.
- `proyecto2-bd1-db/seed.sql`: datos de prueba de ropa formal.
- `proyecto2-bd1-bck/main.py`: API FastAPI.
- `proyecto2-bd1-frt/index.html`: frontend estatico.
- `proyecto2-bd1-frt/assets/`: imagenes genericas descargadas para el catalogo.
- `diseno-bd.md`: modelo ER, modelo relacional y normalizacion.

## Assets

Las imagenes genericas del catalogo fueron descargadas desde Unsplash y guardadas localmente en `proyecto2-bd1-frt/assets/`.
