-- ============================================================
-- DDL - Tienda de Ropa
-- Base de datos: PostgreSQL
-- Usuario: proy2 | Contraseña: secret
-- Fabian Prado Dluzniewski - 23427
-- ============================================================

-- Categoria
CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL,
    descripcion  TEXT
);

-- Proveedor
CREATE TABLE proveedor (
    id_proveedor SERIAL PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    telefono     VARCHAR(20),
    email        VARCHAR(100),
    direccion    TEXT
);

-- Producto
CREATE TABLE producto (
    id_producto    SERIAL PRIMARY KEY,
    nombre         VARCHAR(150) NOT NULL,
    descripcion    TEXT,
    precio_unitario DECIMAL(10,2) NOT NULL,
    stock          INT NOT NULL DEFAULT 0,
    id_categoria   INT NOT NULL REFERENCES categoria(id_categoria),
    id_proveedor   INT NOT NULL REFERENCES proveedor(id_proveedor)
);

-- Empleado
CREATE TABLE empleado (
    id_empleado    SERIAL PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    apellido       VARCHAR(100) NOT NULL,
    puesto         VARCHAR(100) NOT NULL,
    fecha_contrato DATE NOT NULL
);

-- Venta
CREATE TABLE venta (
    id_venta       SERIAL PRIMARY KEY,
    fecha          TIMESTAMP NOT NULL DEFAULT NOW(),
    nombre_cliente VARCHAR(150),
    nit_cliente    VARCHAR(20),
    id_empleado    INT NOT NULL REFERENCES empleado(id_empleado)
);

-- Detalle de venta
CREATE TABLE detalle_venta (
    id_detalle      SERIAL PRIMARY KEY,
    id_venta        INT NOT NULL REFERENCES venta(id_venta),
    id_producto     INT NOT NULL REFERENCES producto(id_producto),
    cantidad        INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL
);

-- Compra a proveedor
CREATE TABLE compra_proveedor (
    id_compra    SERIAL PRIMARY KEY,
    fecha        TIMESTAMP NOT NULL DEFAULT NOW(),
    id_proveedor INT NOT NULL REFERENCES proveedor(id_proveedor)
);

-- Detalle de compra
CREATE TABLE detalle_compra (
    id_detalle    SERIAL PRIMARY KEY,
    id_compra     INT NOT NULL REFERENCES compra_proveedor(id_compra),
    id_producto   INT NOT NULL REFERENCES producto(id_producto),
    cantidad      INT NOT NULL,
    costo_unitario DECIMAL(10,2) NOT NULL
);

-- ============================================================
-- indices justificados
-- ============================================================

-- Busquedas frecuentes de productos por categoria en la UI
CREATE INDEX idx_producto_categoria ON producto(id_categoria);

-- Consultas de historial de ventas filtradas por fecha
CREATE INDEX idx_venta_fecha ON venta(fecha);