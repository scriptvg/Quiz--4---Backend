/*-- ==============================

Base de datos: Libreria - Esquema para biblioteca
Autor: Allan José Veléz González
Fecha: 04/05/2025

Descripción: Esquema para el Quiz #4 - Backend Module

============================== --*/



/*-- ========================================================================
    -- Elimina la base de datos existente para evitar conflictos.
                                
                                ¡Alerta! 
        Crear un backup en producción para esta acción para evitar problemas.

========================================================================= --*/
DROP DATABASE IF EXISTS libreria;

-- Crea la base de datos
CREATE DATABASE libreria
    -- Usa uft8mb4 para caracteres especiales y emojis
    CHARACTER SET utf8mb4
    /* ================================
    -- Usa collation utfmb4_spanich_ci
        ° spanish: Para español
        ° ci: para insensible a
              minusculas y mayusculas
    ================================ */
    COLLATE utf8mb4_spanish_ci;
USE libreria;

SET FOREIGN_KEY_CHECKS = 0;

/* ============================ TABLAS PRINCIPALES ============================*/




-- Tabla de autores
CREATE TABLE autores (
    autor_id                INT AUTO_INCREMENT PRIMARY KEY,                                     -- --> Id único auto incremental
    nombre                  VARCHAR(100)       NOT NULL,                                        -- --> Nombre del autor (obligatorio)
    apellido                VARCHAR(100),                                                       -- --> Apellido del autor (opcional)
    fecha_nacimiento        DATE,                                                               -- --> Fecha de nacimineto ("YYYY-MM-DD")
    fecha_fallecimiento     DATE,                                                               -- --> Fecha de fallecimiento 
    nacionalidad            VARCHAR(50),                                                        -- --> Nacionalidad del autor (opcional)
    sitio_web               VARCHAR(255),                                                       -- --> Url de su sitio web (opcional)
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                                -- --> Fecha de creación 
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP     -- --> Fecha de última modificación
);

-- Tabla de categorías
CREATE TABLE categorias (
    categoria_id               INT AUTO_INCREMENT PRIMARY KEY,                                  -- --> Id único auto incremental (obligatorio)
    nombre VARCHAR(100)        NOT NULL,                                                        -- --> Categoría (Terror, Accion, etc...)
    categoria_padre_id         INT,                                                             -- --> Referecia a categoría padre (para jerarquías en proceso)
    created_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP,                             -- --> Fecha de creación (Tiempo actual)
    updated_at                 TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- --> Fecha de última modificación (Tiempo actual)
    FOREIGN KEY (categoria_padre_id) REFERENCES categorias(categoria_id) ON DELETE SET NULL     -- --> Referencia a la tabla de categorias (esto solo por el momento)
);

/* ============================================================================ */

-- Tabla de libros
CREATE TABLE libros (
    libro_id 					INT AUTO_INCREMENT PRIMARY KEY, 									-- --> Id único auto incremental 
    titulo 						VARCHAR(255) NOT NULL,												-- --> Titúlo del libro (obligatorio)
    subtitulo 					VARCHAR(255),														-- --> Subtitúlo (opcional)
    isbn 						VARCHAR(20) UNIQUE,													-- --> ISBN El International Standard Book Number código (único) internacional para cada libro que lo identifique.
    fecha_publicacion 			DATE,																-- --> Fecha de publicación
    edicion 					VARCHAR(50),														-- --> Edición del libro
    editorial 					VARCHAR(100),														-- --> Editorial
    precio 						DECIMAL(10, 2) NOT NULL,											-- --> Precio del libro (decimal, bytes) - (obligatorio)
    stock 						INT NOT NULL DEFAULT 0,												-- --> Cantidad de libros en stock (obligatorio) - (por defecto = 0)
    descripcion 				TEXT,																-- --> Descripción de los libros
    num_paginas 				INT,																-- --> Número de páginas
    idioma 						VARCHAR(20) DEFAULT 'es',											-- --> Idioma del libro
    calificacion 				DECIMAL(3, 2) DEFAULT 0.00,											-- --> Calificación
    imagen_portada 				VARCHAR(255),														-- --> Imagen de portada
    formato 					VARCHAR(50) DEFAULT 'Digital',										-- --> Formato del libro (por defecto Digital)
    created_at 					TIMESTAMP DEFAULT CURRENT_TIMESTAMP,								-- --> Fecha de creación (Tiempo actual)
    updated_at 					TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP		-- --> Fecha de última modificación (Tiempo actual)
);

/* ============================================================================ */

/* ============================ TABLAS INTERMEDIAS ============================*/

-- Tabla de relación libro-autor
CREATE TABLE libro_autor (
    libro_id 					INT,                                                 -- --> Id del libro
    autor_id 					INT,                                                 -- --> Autor del libro
    PRIMARY KEY (libro_id, autor_id),                                      -- --> Clave primaria compuesta
    FOREIGN KEY (libro_id) REFERENCES libros(libro_id) 	ON DELETE CASCADE, -- --> Clave foranea libro
    FOREIGN KEY (autor_id) REFERENCES autores(autor_id) ON DELETE CASCADE  -- --> Clave foranea autor
);

/* ============================================================================ */

-- Tabla de relación libro-categoría
CREATE TABLE libro_categoria (
    libro_id 				  INT, -- --> Id del libro 
    categoria_id 			INT, -- --> Id de la categoría 
    PRIMARY KEY (libro_id, categoria_id), -- --> Clave primaria compuesta 
    
    FOREIGN KEY (libro_id) 		REFERENCES libros(libro_id) 		      ON DELETE CASCADE, -- --> Clave foranea libro
    FOREIGN KEY (categoria_id) 	REFERENCES categorias(categoria_id) ON DELETE CASCADE  -- --> Clave foranea categoría
);

/* ============================================================================ */

/* ============================ TABLAS CLIENTES - VENTA / DETALLE_VENTA - RESEÑA ============================*/

-- Tabla de clientes
CREATE TABLE clientes (
    cliente_id 			  INT AUTO_INCREMENT PRIMARY KEY, -- --> Id del cliente
    nombre 				    VARCHAR(100) NOT NULL, -- --> Nombre del cliente
    apellido 			    VARCHAR(100) NOT NULL, -- --> Apellido del cliente
    email 				    VARCHAR(100) UNIQUE NOT NULL, -- --> Email del cliente
    password 			  VARCHAR(100) NOT NULL, -- --> Contraseña del cliente
    telefono 			    VARCHAR(20), -- --> Teléfono del cliente
    direccion 			  VARCHAR(255), -- --> Dirección del cliente
    ciudad 				    VARCHAR(100), -- --> Ciudad del cliente
    codigo_postal 		VARCHAR(20), -- --> Código postal del cliente
    pais 				      VARCHAR(50) DEFAULT 'España', -- --> País del cliente
    fecha_registro 		DATE DEFAULT (CURRENT_DATE), -- --> Fecha de registro del cliente
    created_at 			  TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- --> Fecha de creación del cliente
    updated_at 			  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- --> Fecha de última modificación del cliente
);

/* ============================================================================ */

-- Tabla de ventas
CREATE TABLE ventas (
    venta_id 		  INT AUTO_INCREMENT PRIMARY KEY, -- --> Id de la venta
    cliente_id 		INT, -- --> Id del cliente
    fecha_venta 	DATETIME DEFAULT CURRENT_TIMESTAMP, -- --> Fecha de la venta
    total 			  DECIMAL(10, 2) NOT NULL, -- --> Total de la venta
    metodo_pago 	VARCHAR(50), -- --> Método de pago
    estado 			  VARCHAR(50) DEFAULT 'Completada', -- --> Estado de la venta
    created_at 		TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- --> Fecha de creación de la venta
    updated_at 		TIMESTAMP DEFAULT CURRENT_TIMESTAMP 		    ON UPDATE CURRENT_TIMESTAMP, -- --> Fecha de última modificación de la venta
    
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)	ON DELETE SET NULL -- --> Clave foranea cliente
);

/* ============================================================================ */

-- Tabla de detalles de venta
CREATE TABLE detalles_venta (
    detalle_id 			    INT AUTO_INCREMENT PRIMARY KEY, -- --> Id detalle de venta
    venta_id 			      INT, -- --> Id de la venta
    libro_id 			      INT, -- --> Id del libro
    cantidad 			      INT NOT NULL, -- --> Cantidad de libros
    precio_unitario 	  DECIMAL(10, 2) NOT NULL, -- --> Precio unitario del libro
    descuento 			    DECIMAL(5, 2) DEFAULT 0.00, -- --> Descuento aplicado
    created_at 			    TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- --> Fecha de creación de la venta
    updated_at 			    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- --> Fecha de última modificación de la venta
    
    FOREIGN KEY (venta_id) REFERENCES ventas(venta_id) 		ON DELETE CASCADE, -- --> Clave foranea venta
    FOREIGN KEY (libro_id) REFERENCES libros(libro_id) 		ON DELETE SET NULL -- --> Clave foranea libro
);

/* ============================================================================ */

-- Tabla de reseñas
CREATE TABLE resenas (
    resena_id 			  INT AUTO_INCREMENT PRIMARY KEY, -- --> Id de la reseña
    libro_id 			    INT, -- --> Id del libro
    cliente_id 			  INT, -- --> Id del cliente
    calificacion 		  INT NOT NULL CHECK (calificacion BETWEEN 1 AND 5), -- --> Calificación de la reseña
    comentario 			  TEXT, -- --> Comentario de la reseña
    fecha_resena 		  DATETIME DEFAULT CURRENT_TIMESTAMP, -- --> Fecha de la reseña
    created_at 			  TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- --> Fecha de creación de la reseña
    updated_at 			  TIMESTAMP DEFAULT CURRENT_TIMESTAMP 	ON UPDATE CURRENT_TIMESTAMP, -- --> Fecha de última modificación de la reseña
		
    FOREIGN KEY (libro_id) REFERENCES libros(libro_id) 			  ON DELETE CASCADE, -- --> Clave foranea libro
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id) 	ON DELETE CASCADE -- --> Clave foranea cliente
);

SET FOREIGN_KEY_CHECKS = 1;

/* ============================ VISTAS PERSONALIZADAS ============================*/

-- Vista de libros con detalles
CREATE VIEW vista_libros_detallada AS
SELECT 
    l.libro_id,
    l.titulo,
    l.subtitulo,
    l.isbn,
    l.fecha_publicacion,
    l.edicion,
    l.editorial,
    l.precio,
    l.stock,
    l.descripcion,
    l.num_paginas,
    l.idioma,
    l.calificacion,
    l.imagen_portada,
    l.formato,
    GROUP_CONCAT(DISTINCT CONCAT(a.nombre, ' ', a.apellido) SEPARATOR ', ') AS autores,
    GROUP_CONCAT(DISTINCT c.nombre SEPARATOR ', ') AS categorias
FROM 
    libros l
LEFT JOIN 
    libro_autor la ON l.libro_id = la.libro_id
LEFT JOIN 
    autores a ON la.autor_id = a.autor_id
LEFT JOIN 
    libro_categoria lc ON l.libro_id = lc.libro_id
LEFT JOIN 
    categorias c ON lc.categoria_id = c.categoria_id
GROUP BY 
    l.libro_id;

/* ============================================================================ */

-- Vista de ventas con detalles
CREATE VIEW vista_ventas_detallada AS
SELECT 
    v.venta_id,
    v.fecha_venta,
    v.total,
    v.metodo_pago,
    v.estado,
    c.cliente_id,
    CONCAT(c.nombre, ' ', c.apellido) AS cliente,
    c.email,
    COUNT(dv.libro_id) AS num_libros,
    SUM(dv.cantidad) AS cantidad_total
FROM 
    ventas v
JOIN 
    clientes c ON v.cliente_id = c.cliente_id
JOIN 
    detalles_venta dv ON v.venta_id = dv.venta_id
GROUP BY 
    v.venta_id;
    
/* ============================================================================ */

-- Vista de libros más vendidos
CREATE VIEW vista_libros_mas_vendidos AS
SELECT 
    l.libro_id,
    l.titulo,
    SUM(dv.cantidad) AS total_vendidos,
    GROUP_CONCAT(DISTINCT CONCAT(a.nombre, ' ', a.apellido)) AS autores,
    GROUP_CONCAT(DISTINCT c.nombre) AS categorias
FROM 
    detalles_venta dv
JOIN libros l ON dv.libro_id = l.libro_id
LEFT JOIN libro_autor la ON l.libro_id = la.libro_id
LEFT JOIN autores a ON la.autor_id = a.autor_id
LEFT JOIN libro_categoria lc ON l.libro_id = lc.libro_id
LEFT JOIN categorias c ON lc.categoria_id = c.categoria_id
GROUP BY l.libro_id
ORDER BY total_vendidos DESC;

/* ============================================================================ */

-- Ventas del mes por cliente
CREATE VIEW vista_ventas_mensuales_cliente AS
SELECT 
    c.cliente_id,
    CONCAT(c.nombre, ' ', c.apellido) AS cliente,
    DATE_FORMAT(v.fecha_venta, '%Y-%m') AS mes,
    COUNT(v.venta_id) AS cantidad_ventas,
    SUM(v.total) AS total_comprado
FROM ventas v
JOIN clientes c ON v.cliente_id = c.cliente_id
GROUP BY c.cliente_id, mes
ORDER BY mes DESC;



/* ============================ PROCESOS ALMACENADOS ============================*/

-- Procedimiento para actualizar stock
DELIMITER //
CREATE PROCEDURE actualizar_stock(
    IN p_libro_id INT,
    IN p_cantidad INT
)
BEGIN
    UPDATE libros
    SET stock = stock + p_cantidad
    WHERE libro_id = p_libro_id;
    
    -- Registrar si el stock es bajo
    IF (SELECT stock FROM libros WHERE libro_id = p_libro_id) < 5 THEN
        INSERT INTO log_eventos (tipo, mensaje)
        VALUES ('stock_bajo', CONCAT('Stock bajo para libro ID: ', p_libro_id, '. Stock actual: ', 
                (SELECT stock FROM libros WHERE libro_id = p_libro_id)));
    END IF;
END //
DELIMITER ;

/* ============================================================================ */

-- Procedimiento para reaizar venta
DELIMITER //
CREATE PROCEDURE registrar_venta(
    IN p_cliente_id INT,
    IN p_metodo_pago VARCHAR(50),
    IN p_libro_id INT,
    IN p_cantidad INT,
    IN p_precio_unitario DECIMAL(10,2),
    IN p_descuento DECIMAL(5,2)
)
BEGIN
    DECLARE v_total DECIMAL(10,2);
    
    SET v_total = (p_precio_unitario * p_cantidad) - (p_precio_unitario * p_cantidad * p_descuento / 100);

    -- Crear venta
    INSERT INTO ventas(cliente_id, total, metodo_pago)
    VALUES (p_cliente_id, v_total, p_metodo_pago);

    -- Obtener ID de la venta insertada
    SET @ultima_venta_id = LAST_INSERT_ID();

    -- Insertar detalle
    INSERT INTO detalles_venta(venta_id, libro_id, cantidad, precio_unitario, descuento)
    VALUES (@ultima_venta_id, p_libro_id, p_cantidad, p_precio_unitario, p_descuento);

    -- El trigger se encarga de actualizar el stock
END //
DELIMITER ;

/* ============================================================================ */

-- Procedimineto para el total de ventas por autor
DELIMITER //
CREATE PROCEDURE total_ventas_autor(IN p_autor_id INT)
BEGIN
    SELECT 
        a.autor_id,
        CONCAT(a.nombre, ' ', a.apellido) AS autor,
        SUM(dv.cantidad * dv.precio_unitario) AS total_ventas
    FROM autores a
    JOIN libro_autor la ON a.autor_id = la.autor_id
    JOIN detalles_venta dv ON la.libro_id = dv.libro_id
    WHERE a.autor_id = p_autor_id
    GROUP BY a.autor_id;
END //
DELIMITER ;

/* ============================================================================ */

-- Procedimiento para buscar libros
DELIMITER //
CREATE PROCEDURE buscar_libros(
    IN p_termino VARCHAR(255)
)
BEGIN
    SELECT 
        l.libro_id,
        l.titulo,
        l.subtitulo,
        l.isbn,
        l.editorial,
        l.precio,
        l.stock,
        l.calificacion,
        GROUP_CONCAT(DISTINCT CONCAT(a.nombre, ' ', a.apellido) SEPARATOR ', ') AS autores,
        GROUP_CONCAT(DISTINCT c.nombre SEPARATOR ', ') AS categorias
    FROM 
        libros l
    LEFT JOIN 
        libro_autor la ON l.libro_id = la.libro_id
    LEFT JOIN 
        autores a ON la.autor_id = a.autor_id
    LEFT JOIN 
        libro_categoria lc ON l.libro_id = lc.libro_id
    LEFT JOIN 
        categorias c ON lc.categoria_id = c.categoria_id
    WHERE 
        l.titulo LIKE CONCAT('%', p_termino, '%') OR
        l.subtitulo LIKE CONCAT('%', p_termino, '%') OR
        l.isbn LIKE CONCAT('%', p_termino, '%') OR
        l.editorial LIKE CONCAT('%', p_termino, '%') OR
        l.descripcion LIKE CONCAT('%', p_termino, '%') OR
        CONCAT(a.nombre, ' ', a.apellido) LIKE CONCAT('%', p_termino, '%') OR
        c.nombre LIKE CONCAT('%', p_termino, '%')
    GROUP BY 
        l.libro_id;
END //
DELIMITER ;

/* ============================================================================ */



/* ============================ TABLAS DE LOGS ============================*/

-- Tabla de log de eventos
CREATE TABLE log_eventos (
    evento_id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/* ============================================================================ */



/* ============================ TRIGGERS ============================*/

-- Trigger para actualizar stock después de una venta
DELIMITER //
CREATE TRIGGER after_venta_insert
AFTER INSERT ON detalles_venta
FOR EACH ROW
BEGIN
    -- Reducir el stock
    UPDATE libros
    SET stock = stock - NEW.cantidad
    WHERE libro_id = NEW.libro_id;
    
    -- Verificar si el stock es bajo después de la venta
    IF (SELECT stock FROM libros WHERE libro_id = NEW.libro_id) < 5 THEN
        INSERT INTO log_eventos (tipo, mensaje)
        VALUES ('stock_bajo', CONCAT('Stock bajo para libro ID: ', NEW.libro_id, 
                '. Stock actual: ', (SELECT stock FROM libros WHERE libro_id = NEW.libro_id)));
    END IF;
END //
DELIMITER ;

/* ============================================================================ */

-- Trigger para actualizar la calificación promedio del libro después de una reseña
DELIMITER //
CREATE TRIGGER after_resena_insert
AFTER INSERT ON resenas
FOR EACH ROW
BEGIN
    UPDATE libros l
    SET l.calificacion = (
        SELECT AVG(r.calificacion)
        FROM resenas r
        WHERE r.libro_id = NEW.libro_id
    )
    WHERE l.libro_id = NEW.libro_id;
END //
DELIMITER ;

/* ============================================================================ */

-- Trigger para el log movimientos de log
DELIMITER //
CREATE TRIGGER after_cliente_delete
AFTER DELETE ON clientes
FOR EACH ROW
BEGIN
    INSERT INTO log_table(entidad, descripcion)
    VALUES (
        'cliente',
        CONCAT('Se eliminó cliente ID: ', OLD.cliente_id, ' - ', OLD.nombre, ' ', OLD.apellido)
    );
END //
DELIMITER ;




/* ============================ INDICES DE BUSQUEDA ============================*/

-- Índices para mejorar el rendimiento
CREATE INDEX idx_libros_titulo ON libros(titulo);
CREATE INDEX idx_libros_isbn ON libros(isbn);
CREATE INDEX idx_autores_nombre ON autores(nombre, apellido);
CREATE INDEX idx_categorias_nombre ON categorias(nombre);
CREATE INDEX idx_clientes_email ON clientes(email);
CREATE INDEX idx_ventas_fecha ON ventas(fecha_venta);

/* ============================================================================ */