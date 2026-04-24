-- ============================================================
-- SEED - Tienda de Ropa
-- seed.sql
-- ============================================================

-- Categorias (6 registros)
INSERT INTO categoria (nombre, descripcion) VALUES
('Camisas',     'Camisas formales e informales para hombre y mujer'),
('Pantalones',  'Pantalones de vestir, jeans y casuales'),
('Vestidos',    'Vestidos de dia, noche y ocasiones especiales'),
('Ropa interior','Ropa interior y pijamas para adultos'),
('Accesorios',  'Cinturones, gorras, bufandas y complementos'),
('Abrigos',     'Chaquetas, abrigos y ropa de temporada fria');

-- Proveedores (6 registros)
INSERT INTO proveedor (nombre, telefono, email, direccion) VALUES
('Textiles del Norte S.A.',  '22341100', 'ventas@textilesnorte.com',  '12 Calle 5-67, Zona 1, Guatemala'),
('Confecciones Maya Ltda.',  '23456789', 'info@confeccionesmaya.com', 'Av. Reforma 8-45, Zona 9, Guatemala'),
('Importadora Zentex',       '24567890', 'pedidos@zentex.com',        '6a Av. 12-30, Zona 10, Guatemala'),
('Distribuidora Atlantida',  '25678901', 'contacto@atlantida.com',    'Calzada Roosevelt 22-15, Zona 7'),
('Moda Express Guatemala',   '26789012', 'moda@expressguat.com',      '5a Calle 10-20, Zona 4, Guatemala'),
('Telas y Mas S.A.',         '27890123', 'telas@telasmas.com',        'Blvd. Los Proceres 18-22, Zona 10');

-- Productos (25 registros)
INSERT INTO producto (nombre, descripcion, precio_unitario, stock, id_categoria, id_proveedor) VALUES
('Camisa Oxford Blanca',       'Camisa formal de algodon, talla M',         189.99,  40, 1, 1),
('Camisa Polo Azul',           'Camisa polo casual manga corta',             149.99,  55, 1, 2),
('Camisa Lino Beige',          'Camisa de lino para clima calido',           169.99,  30, 1, 3),
('Camisa Cuadros Flannel',     'Camisa flannel estilo leñador',              129.99,  60, 1, 4),
('Pantalon Vestir Negro',      'Pantalon de vestir corte recto',             249.99,  35, 2, 1),
('Jean Slim Azul',             'Jean slim fit lavado medio',                 219.99,  80, 2, 2),
('Jean Clasico Oscuro',        'Jean corte clasico color oscuro',            199.99,  70, 2, 3),
('Pantalon Chino Khaki',       'Pantalon chino color khaki',                 189.99,  45, 2, 5),
('Vestido Floral Verano',      'Vestido estampado floral manga sisa',        279.99,  25, 3, 2),
('Vestido Negro Formal',       'Vestido negro largo para eventos',           399.99,  15, 3, 6),
('Vestido Casual Rayas',       'Vestido casual a rayas multicolor',          229.99,  30, 3, 4),
('Vestido Midi Rojo',          'Vestido midi color rojo vivo',               319.99,  20, 3, 2),
('Pack Boxer x3',              'Pack de 3 boxers algodon peinado',           129.99, 100, 4, 5),
('Pijama Set Franela',         'Conjunto pijama franela hombre',             189.99,  40, 4, 1),
('Pijama Mujer Saten',         'Conjunto pijama saten mujer',                209.99,  35, 4, 6),
('Pack Calcetines x6',         'Pack 6 pares calcetines algodon',             79.99, 120, 4, 5),
('Cinturon Cuero Negro',       'Cinturon de cuero genuino negro',            149.99,  50, 5, 3),
('Gorra Bordada',              'Gorra con bordado logo tienda',               89.99,  75, 5, 4),
('Bufanda Lana Gris',          'Bufanda de lana suave color gris',           119.99,  30, 5, 6),
('Bolso Tote Canvas',          'Bolso tote de canvas natural',               179.99,  40, 5, 2),
('Chaqueta Denim Azul',        'Chaqueta de mezclilla clasica',              349.99,  25, 6, 3),
('Abrigo Lana Camel',          'Abrigo largo lana color camel',              599.99,  10, 6, 6),
('Chaqueta Bomber Verde',      'Chaqueta bomber estilo militar',             429.99,  18, 6, 5),
('Chaleco Acolchado Negro',    'Chaleco acolchado sin mangas',               299.99,  22, 6, 1),
('Parka Impermeable Azul',     'Parka impermeable con capucha',              549.99,  12, 6, 4);

-- Empleados (6 registros)
INSERT INTO empleado (nombre, apellido, puesto, fecha_contrato) VALUES
('Carlos',    'Mendoza',   'Vendedor',        '2023-01-15'),
('Lucia',     'Ramirez',   'Vendedora',       '2022-06-01'),
('Diego',     'Perez',     'Supervisor',      '2021-03-10'),
('Valeria',   'Lopez',     'Vendedora',       '2023-08-20'),
('Andres',    'Garcia',    'Vendedor',        '2024-01-05'),
('Sofia',     'Herrera',   'Administradora',  '2020-11-12');

-- Ventas (15 registros)
INSERT INTO venta (fecha, nombre_cliente, nit_cliente, id_empleado) VALUES
('2025-01-05 10:30:00', 'Maria Gonzalez',   '1234567-8', 1),
('2025-01-08 11:00:00', 'Roberto Castillo', '8765432-1', 2),
('2025-01-10 14:20:00', NULL,               'CF',        1),
('2025-01-12 09:45:00', 'Ana Morales',      '5432109-3', 3),
('2025-01-15 16:00:00', NULL,               'CF',        4),
('2025-02-02 10:15:00', 'Pedro Juarez',     '9876543-2', 2),
('2025-02-10 13:30:00', 'Laura Vasquez',    '3456789-0', 1),
('2025-02-14 15:00:00', NULL,               'CF',        5),
('2025-02-20 11:45:00', 'Jorge Soto',       '6543210-9', 3),
('2025-03-01 09:00:00', 'Carmen Ruiz',      '2109876-5', 2),
('2025-03-05 12:30:00', NULL,               'CF',        4),
('2025-03-10 14:00:00', 'Luis Flores',      '7890123-4', 1),
('2025-03-15 16:30:00', 'Elena Torres',     '4321098-7', 5),
('2025-03-20 10:00:00', NULL,               'CF',        3),
('2025-03-25 11:15:00', 'Ricardo Molina',   '0987654-3', 2);

-- Detalle de ventas (25 registros)
INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES
(1,  1,  2, 189.99),
(1,  5,  1, 249.99),
(2,  9,  1, 279.99),
(2, 17,  1, 149.99),
(3,  6,  1, 219.99),
(4, 10,  1, 399.99),
(4, 19,  1, 119.99),
(5, 13,  2, 129.99),
(5, 16,  1,  79.99),
(6,  2,  3, 149.99),
(7, 11,  1, 229.99),
(7,  8,  1, 189.99),
(8, 21,  1, 349.99),
(9,  7,  2, 199.99),
(9, 18,  1,  89.99),
(10, 12, 1, 319.99),
(10, 20, 1, 179.99),
(11,  3, 2, 169.99),
(12, 22, 1, 599.99),
(12, 19, 1, 119.99),
(13, 23, 1, 429.99),
(13, 15, 1, 209.99),
(14,  4, 2, 129.99),
(15, 24, 1, 299.99),
(15,  6, 1, 219.99);

-- Compras a proveedor (6 registros)
INSERT INTO compra_proveedor (fecha, id_proveedor) VALUES
('2025-01-03 08:00:00', 1),
('2025-01-20 09:30:00', 2),
('2025-02-05 10:00:00', 3),
('2025-02-18 08:45:00', 4),
('2025-03-02 09:00:00', 5),
('2025-03-18 10:30:00', 6);

-- Detalle de compras (25 registros)
INSERT INTO detalle_compra (id_compra, id_producto, cantidad, costo_unitario) VALUES
(1,  1, 20,  95.00),
(1,  5, 15, 125.00),
(1, 14, 20,  95.00),
(1, 24, 10, 149.00),
(2,  9, 15, 139.00),
(2, 11, 15, 114.00),
(2, 12, 10, 159.00),
(2, 20, 20,  89.00),
(3,  3, 15,  84.00),
(3,  7, 20,  99.00),
(3, 17, 25,  74.00),
(3, 21, 10, 174.00),
(4,  4, 30,  64.00),
(4,  8, 20,  94.00),
(4, 18, 35,  44.00),
(4, 25, 10, 274.00),
(5,  2, 25,  74.00),
(5, 13, 50,  64.00),
(5, 16, 60,  39.00),
(5, 23, 10, 214.00),
(6, 10, 10, 199.00),
(6, 15, 15, 104.00),
(6, 19, 15,  59.00),
(6, 22, 5,  299.00),
(6,  6, 25, 109.00);