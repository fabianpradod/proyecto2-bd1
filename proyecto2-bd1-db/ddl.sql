DROP VIEW IF EXISTS vw_resumen_ventas;
DROP TABLE IF EXISTS detalle_compra CASCADE;
DROP TABLE IF EXISTS compra_proveedor CASCADE;
DROP TABLE IF EXISTS detalle_venta CASCADE;
DROP TABLE IF EXISTS venta CASCADE;
DROP TABLE IF EXISTS producto CASCADE;
DROP TABLE IF EXISTS empleado CASCADE;
DROP TABLE IF EXISTS proveedor CASCADE;
DROP TABLE IF EXISTS categoria CASCADE;

CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    descripcion  TEXT NOT NULL,
    activo       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE proveedor (
    id_proveedor SERIAL PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL UNIQUE,
    contacto     VARCHAR(120) NOT NULL,
    telefono     VARCHAR(20) NOT NULL,
    email        VARCHAR(120) NOT NULL,
    direccion    TEXT NOT NULL,
    activo       BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE empleado (
    id_empleado    SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    apellido       VARCHAR(100) NOT NULL,
    puesto         VARCHAR(100) NOT NULL,
    fecha_contrato DATE NOT NULL,
    activo         BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE producto (
    id_producto     SERIAL PRIMARY KEY,
    sku             VARCHAR(40) NOT NULL UNIQUE,
    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT NOT NULL,
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    stock           INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    talla           VARCHAR(20) NOT NULL,
    color           VARCHAR(60) NOT NULL,
    imagen_url      VARCHAR(255),
    activo          BOOLEAN NOT NULL DEFAULT TRUE,
    actualizado_en  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_categoria    INTEGER NOT NULL REFERENCES categoria(id_categoria),
    id_proveedor    INTEGER NOT NULL REFERENCES proveedor(id_proveedor)
);

CREATE TABLE venta (
    id_venta       SERIAL PRIMARY KEY,
    fecha          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nombre_cliente VARCHAR(150) NOT NULL,
    nit_cliente    VARCHAR(20) NOT NULL DEFAULT 'CF',
    canal          VARCHAR(30) NOT NULL CHECK (canal IN ('tienda', 'web', 'telefono')),
    id_empleado    INTEGER NOT NULL REFERENCES empleado(id_empleado)
);

CREATE TABLE detalle_venta (
    id_detalle      SERIAL PRIMARY KEY,
    id_venta        INTEGER NOT NULL REFERENCES venta(id_venta) ON DELETE CASCADE,
    id_producto     INTEGER NOT NULL REFERENCES producto(id_producto),
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0)
);

CREATE TABLE compra_proveedor (
    id_compra    SERIAL PRIMARY KEY,
    fecha        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    documento    VARCHAR(40) NOT NULL UNIQUE,
    id_proveedor INTEGER NOT NULL REFERENCES proveedor(id_proveedor)
);

CREATE TABLE detalle_compra (
    id_detalle     SERIAL PRIMARY KEY,
    id_compra      INTEGER NOT NULL REFERENCES compra_proveedor(id_compra) ON DELETE CASCADE,
    id_producto    INTEGER NOT NULL REFERENCES producto(id_producto),
    cantidad       INTEGER NOT NULL CHECK (cantidad > 0),
    costo_unitario NUMERIC(10,2) NOT NULL CHECK (costo_unitario > 0)
);

CREATE VIEW vw_resumen_ventas AS
SELECT
    v.id_venta,
    v.fecha,
    v.nombre_cliente,
    v.nit_cliente,
    v.canal,
    e.nombre || ' ' || e.apellido AS empleado,
    COUNT(dv.id_detalle) AS lineas,
    COALESCE(SUM(dv.cantidad), 0) AS unidades,
    COALESCE(SUM(dv.cantidad * dv.precio_unitario), 0)::NUMERIC(10,2) AS total
FROM venta v
JOIN empleado e ON e.id_empleado = v.id_empleado
LEFT JOIN detalle_venta dv ON dv.id_venta = v.id_venta
GROUP BY
    v.id_venta,
    v.fecha,
    v.nombre_cliente,
    v.nit_cliente,
    v.canal,
    e.nombre,
    e.apellido;

CREATE INDEX idx_producto_categoria ON producto(id_categoria);

CREATE INDEX idx_venta_fecha ON venta(fecha);

CREATE INDEX idx_detalle_venta_producto ON detalle_venta(id_producto);

CREATE INDEX idx_producto_nombre_lower ON producto(LOWER(nombre));
