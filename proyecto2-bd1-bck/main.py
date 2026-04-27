from __future__ import annotations

import csv
import io
import os
from decimal import Decimal
from typing import Any, Literal

import psycopg
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row
from pydantic import BaseModel, Field


def _database_url() -> str:
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    user = os.getenv("POSTGRES_USER", "proy2")
    password = os.getenv("POSTGRES_PASSWORD", "secret")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "55432")
    db = os.getenv("POSTGRES_DB", "proyecto2_bd")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def get_connection() -> psycopg.Connection:
    conn = psycopg.connect(_database_url(), row_factory=dict_row)
    conn.autocommit = True
    return conn


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def execute_returning(sql: str, params: tuple[Any, ...]) -> dict[str, Any]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Ya existe un registro con esos datos unicos.") from exc
    except psycopg.errors.ForeignKeyViolation as exc:
        raise HTTPException(status_code=400, detail="La categoria o proveedor seleccionado no existe.") from exc

    if row is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")
    return row


class CategoryPayload(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: str = Field(..., min_length=3)
    activo: bool = True


class ProductPayload(BaseModel):
    sku: str = Field(..., min_length=3, max_length=40)
    nombre: str = Field(..., min_length=2, max_length=150)
    descripcion: str = Field(..., min_length=3)
    precio_unitario: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    talla: str = Field(..., min_length=1, max_length=20)
    color: str = Field(..., min_length=2, max_length=60)
    imagen_url: str | None = Field(default=None, max_length=255)
    activo: bool = True
    id_categoria: int = Field(..., gt=0)
    id_proveedor: int = Field(..., gt=0)


class SaleLinePayload(BaseModel):
    id_producto: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)


class SalePayload(BaseModel):
    nombre_cliente: str = Field(..., min_length=2, max_length=150)
    nit_cliente: str = Field(default="CF", min_length=2, max_length=20)
    canal: Literal["tienda", "web", "telefono"] = "tienda"
    id_empleado: int = Field(..., gt=0)
    detalles: list[SaleLinePayload] = Field(..., min_length=1)


app = FastAPI(
    title="Atelier Formal API",
    version="1.0.0",
    description="API academica para inventario, ventas y reportes de una tienda de ropa formal.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "Atelier Formal API", "status": "ok"}


@app.get("/api/health")
def health() -> dict[str, str]:
    row = fetch_one("SELECT CURRENT_DATABASE() AS database_name;")
    return {"status": "ok", "database": row["database_name"] if row else "unknown"}


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    stats = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM producto WHERE activo = TRUE) AS productos_activos,
            (SELECT COUNT(*) FROM categoria WHERE activo = TRUE) AS categorias_activas,
            (SELECT COUNT(*) FROM proveedor WHERE activo = TRUE) AS proveedores_activos,
            (SELECT COALESCE(SUM(total), 0)::NUMERIC(10,2) FROM vw_resumen_ventas) AS ventas_historicas,
            (SELECT COUNT(*) FROM producto WHERE activo = TRUE AND stock <= 10) AS productos_bajo_stock;
        """
    )
    recent_sales = fetch_all(
        """
        SELECT id_venta, fecha, nombre_cliente, canal, empleado, unidades, total
        FROM vw_resumen_ventas
        ORDER BY fecha DESC
        LIMIT 5;
        """
    )
    return {"stats": stats or {}, "recent_sales": recent_sales}


@app.get("/api/categories")
def list_categories() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            c.id_categoria,
            c.nombre,
            c.descripcion,
            c.activo,
            COUNT(p.id_producto) FILTER (WHERE p.activo = TRUE) AS productos_activos
        FROM categoria c
        LEFT JOIN producto p ON p.id_categoria = c.id_categoria
        GROUP BY c.id_categoria, c.nombre, c.descripcion, c.activo
        ORDER BY c.activo DESC, c.nombre ASC;
        """
    )


@app.get("/api/categories/{category_id}")
def get_category(category_id: int) -> dict[str, Any]:
    row = fetch_one(
        """
        SELECT id_categoria, nombre, descripcion, activo
        FROM categoria
        WHERE id_categoria = %s;
        """,
        (category_id,),
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada.")
    return row


@app.post("/api/categories", status_code=201)
def create_category(payload: CategoryPayload) -> dict[str, Any]:
    return execute_returning(
        """
        INSERT INTO categoria (nombre, descripcion, activo)
        VALUES (%s, %s, %s)
        RETURNING id_categoria, nombre, descripcion, activo;
        """,
        (payload.nombre.strip(), payload.descripcion.strip(), payload.activo),
    )


@app.put("/api/categories/{category_id}")
def update_category(category_id: int, payload: CategoryPayload) -> dict[str, Any]:
    return execute_returning(
        """
        UPDATE categoria
        SET nombre = %s,
            descripcion = %s,
            activo = %s
        WHERE id_categoria = %s
        RETURNING id_categoria, nombre, descripcion, activo;
        """,
        (payload.nombre.strip(), payload.descripcion.strip(), payload.activo, category_id),
    )


@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int) -> dict[str, Any]:
    return execute_returning(
        """
        UPDATE categoria
        SET activo = FALSE
        WHERE id_categoria = %s
        RETURNING id_categoria, nombre, descripcion, activo;
        """,
        (category_id,),
    )


@app.get("/api/suppliers")
def list_suppliers() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id_proveedor, nombre, contacto, telefono, email, direccion, activo
        FROM proveedor
        ORDER BY activo DESC, nombre ASC;
        """
    )


@app.get("/api/employees")
def list_employees() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id_empleado, nombre, apellido, puesto, fecha_contrato, activo
        FROM empleado
        WHERE activo = TRUE
        ORDER BY apellido ASC, nombre ASC;
        """
    )


@app.get("/api/products")
def list_products(
    q: str | None = Query(default=None, max_length=80),
    category_id: int | None = Query(default=None, gt=0),
    active_only: bool = Query(default=False),
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if active_only:
        conditions.append("p.activo = TRUE")
    if q:
        conditions.append("(LOWER(p.nombre) LIKE LOWER(%s) OR LOWER(p.sku) LIKE LOWER(%s))")
        like = f"%{q.strip()}%"
        params.extend([like, like])
    if category_id:
        conditions.append("p.id_categoria = %s")
        params.append(category_id)

    where_sql = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return fetch_all(
        f"""
        SELECT
            p.id_producto,
            p.sku,
            p.nombre,
            p.descripcion,
            p.precio_unitario,
            p.stock,
            p.talla,
            p.color,
            p.imagen_url,
            p.activo,
            p.actualizado_en,
            p.id_categoria,
            c.nombre AS categoria,
            p.id_proveedor,
            pr.nombre AS proveedor
        FROM producto p
        JOIN categoria c ON c.id_categoria = p.id_categoria
        JOIN proveedor pr ON pr.id_proveedor = p.id_proveedor
        {where_sql}
        ORDER BY p.activo DESC, p.nombre ASC;
        """,
        tuple(params),
    )


@app.get("/api/products/{product_id}")
def get_product(product_id: int) -> dict[str, Any]:
    row = fetch_one(
        """
        SELECT
            p.id_producto,
            p.sku,
            p.nombre,
            p.descripcion,
            p.precio_unitario,
            p.stock,
            p.talla,
            p.color,
            p.imagen_url,
            p.activo,
            p.id_categoria,
            c.nombre AS categoria,
            p.id_proveedor,
            pr.nombre AS proveedor
        FROM producto p
        JOIN categoria c ON c.id_categoria = p.id_categoria
        JOIN proveedor pr ON pr.id_proveedor = p.id_proveedor
        WHERE p.id_producto = %s;
        """,
        (product_id,),
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return row


@app.post("/api/products", status_code=201)
def create_product(payload: ProductPayload) -> dict[str, Any]:
    return execute_returning(
        """
        INSERT INTO producto (
            sku, nombre, descripcion, precio_unitario, stock, talla, color,
            imagen_url, activo, id_categoria, id_proveedor
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id_producto, sku, nombre, descripcion, precio_unitario, stock,
                  talla, color, imagen_url, activo, id_categoria, id_proveedor;
        """,
        (
            payload.sku.strip().upper(),
            payload.nombre.strip(),
            payload.descripcion.strip(),
            payload.precio_unitario,
            payload.stock,
            payload.talla.strip(),
            payload.color.strip(),
            payload.imagen_url,
            payload.activo,
            payload.id_categoria,
            payload.id_proveedor,
        ),
    )


@app.put("/api/products/{product_id}")
def update_product(product_id: int, payload: ProductPayload) -> dict[str, Any]:
    return execute_returning(
        """
        UPDATE producto
        SET sku = %s,
            nombre = %s,
            descripcion = %s,
            precio_unitario = %s,
            stock = %s,
            talla = %s,
            color = %s,
            imagen_url = %s,
            activo = %s,
            id_categoria = %s,
            id_proveedor = %s,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE id_producto = %s
        RETURNING id_producto, sku, nombre, descripcion, precio_unitario, stock,
                  talla, color, imagen_url, activo, id_categoria, id_proveedor;
        """,
        (
            payload.sku.strip().upper(),
            payload.nombre.strip(),
            payload.descripcion.strip(),
            payload.precio_unitario,
            payload.stock,
            payload.talla.strip(),
            payload.color.strip(),
            payload.imagen_url,
            payload.activo,
            payload.id_categoria,
            payload.id_proveedor,
            product_id,
        ),
    )


@app.delete("/api/products/{product_id}")
def delete_product(product_id: int) -> dict[str, Any]:
    return execute_returning(
        """
        UPDATE producto
        SET activo = FALSE,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE id_producto = %s
        RETURNING id_producto, sku, nombre, activo;
        """,
        (product_id,),
    )


@app.post("/api/sales", status_code=201)
def create_sale(payload: SalePayload) -> dict[str, Any]:
    conn = get_connection()
    total = Decimal("0")

    try:
        conn.execute("BEGIN;")
        employee = conn.execute(
            "SELECT id_empleado FROM empleado WHERE id_empleado = %s AND activo = TRUE;",
            (payload.id_empleado,),
        ).fetchone()
        if employee is None:
            raise HTTPException(status_code=400, detail="Empleado no encontrado o inactivo.")

        sale_row = conn.execute(
            """
            INSERT INTO venta (nombre_cliente, nit_cliente, canal, id_empleado)
            VALUES (%s, %s, %s, %s)
            RETURNING id_venta, fecha;
            """,
            (
                payload.nombre_cliente.strip(),
                payload.nit_cliente.strip().upper(),
                payload.canal,
                payload.id_empleado,
            ),
        ).fetchone()

        for line in payload.detalles:
            product = conn.execute(
                """
                SELECT id_producto, nombre, precio_unitario, stock
                FROM producto
                WHERE id_producto = %s AND activo = TRUE
                FOR UPDATE;
                """,
                (line.id_producto,),
            ).fetchone()
            if product is None:
                raise HTTPException(status_code=404, detail=f"Producto {line.id_producto} no encontrado.")
            if product["stock"] < line.cantidad:
                raise HTTPException(
                    status_code=409,
                    detail=f"Stock insuficiente para {product['nombre']}. Disponible: {product['stock']}.",
                )

            conn.execute(
                """
                INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s);
                """,
                (sale_row["id_venta"], line.id_producto, line.cantidad, product["precio_unitario"]),
            )
            conn.execute(
                """
                UPDATE producto
                SET stock = stock - %s,
                    actualizado_en = CURRENT_TIMESTAMP
                WHERE id_producto = %s;
                """,
                (line.cantidad, line.id_producto),
            )
            total += Decimal(product["precio_unitario"]) * line.cantidad

        conn.execute("COMMIT;")
        return {
            "id_venta": sale_row["id_venta"],
            "fecha": sale_row["fecha"],
            "lineas": len(payload.detalles),
            "total": total,
        }
    except HTTPException:
        conn.execute("ROLLBACK;")
        raise
    except Exception as exc:
        conn.execute("ROLLBACK;")
        raise HTTPException(status_code=500, detail="No se pudo registrar la venta.") from exc
    finally:
        conn.close()


@app.get("/api/reports/sales-summary")
def sales_summary(limit: int = Query(default=20, ge=1, le=100)) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT id_venta, fecha, nombre_cliente, nit_cliente, canal, empleado, lineas, unidades, total
        FROM vw_resumen_ventas
        ORDER BY fecha DESC
        LIMIT %s;
        """,
        (limit,),
    )


def category_performance_rows() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            c.id_categoria,
            c.nombre AS categoria,
            COUNT(DISTINCT v.id_venta) AS ventas,
            SUM(dv.cantidad) AS unidades,
            SUM(dv.cantidad * dv.precio_unitario)::NUMERIC(10,2) AS total,
            ROUND(AVG(dv.precio_unitario), 2) AS precio_promedio
        FROM categoria c
        JOIN producto p ON p.id_categoria = c.id_categoria
        JOIN detalle_venta dv ON dv.id_producto = p.id_producto
        JOIN venta v ON v.id_venta = dv.id_venta
        GROUP BY c.id_categoria, c.nombre
        HAVING SUM(dv.cantidad * dv.precio_unitario) > 0
        ORDER BY total DESC;
        """
    )


@app.get("/api/reports/category-performance")
def category_performance() -> list[dict[str, Any]]:
    return category_performance_rows()


@app.get("/api/reports/category-performance.csv")
def category_performance_csv() -> Response:
    rows = category_performance_rows()
    buffer = io.StringIO()
    fieldnames = ["id_categoria", "categoria", "ventas", "unidades", "total", "precio_promedio"]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key) for key in fieldnames})

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=reporte_categorias.csv"},
    )


@app.get("/api/reports/top-products")
def top_products() -> list[dict[str, Any]]:
    return fetch_all(
        """
        WITH ventas_producto AS (
            SELECT
                p.id_producto,
                p.sku,
                p.nombre,
                c.nombre AS categoria,
                SUM(dv.cantidad) AS unidades,
                SUM(dv.cantidad * dv.precio_unitario)::NUMERIC(10,2) AS total
            FROM producto p
            JOIN categoria c ON c.id_categoria = p.id_categoria
            JOIN detalle_venta dv ON dv.id_producto = p.id_producto
            GROUP BY p.id_producto, p.sku, p.nombre, c.nombre
        ),
        ranking AS (
            SELECT
                ventas_producto.*,
                DENSE_RANK() OVER (ORDER BY total DESC) AS posicion
            FROM ventas_producto
        )
        SELECT id_producto, sku, nombre, categoria, unidades, total, posicion
        FROM ranking
        WHERE posicion <= 10
        ORDER BY posicion ASC, nombre ASC;
        """
    )


@app.get("/api/reports/reorder-suggestions")
def reorder_suggestions() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            p.id_producto,
            p.sku,
            p.nombre,
            c.nombre AS categoria,
            p.stock,
            (
                SELECT ROUND(AVG(p2.stock), 2)
                FROM producto p2
                WHERE p2.id_categoria = p.id_categoria
                  AND p2.activo = TRUE
            ) AS stock_promedio_categoria
        FROM producto p
        JOIN categoria c ON c.id_categoria = p.id_categoria
        WHERE p.activo = TRUE
          AND p.id_producto IN (
              SELECT p3.id_producto
              FROM producto p3
              WHERE p3.stock <= 15
          )
        ORDER BY p.stock ASC, p.nombre ASC;
        """
    )


@app.get("/api/reports/unsold-products")
def unsold_products() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            p.id_producto,
            p.sku,
            p.nombre,
            c.nombre AS categoria,
            p.stock,
            p.precio_unitario
        FROM producto p
        JOIN categoria c ON c.id_categoria = p.id_categoria
        WHERE p.activo = TRUE
          AND NOT EXISTS (
              SELECT 1
              FROM detalle_venta dv
              WHERE dv.id_producto = p.id_producto
          )
        ORDER BY p.nombre ASC;
        """
    )
