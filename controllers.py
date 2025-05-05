from db_manager import DatabaseManager
from models import Libro, Autor, Categoria, Cliente, Venta, DetalleVenta, Resena

class LibroController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def obtener_todos(self):
        """Obtiene todos los libros con sus autores y categorías"""
        self.db.connect()
        libros = self.db.fetch_all("SELECT * FROM vista_libros_detallada")
        self.db.disconnect()
        return libros
    
    def obtener_por_id(self, libro_id):
        """Obtiene un libro por su ID"""
        self.db.connect()
        libro = self.db.fetch_one("SELECT * FROM vista_libros_detallada WHERE libro_id = %s", (libro_id,))
        self.db.disconnect()
        return libro
    
    def buscar(self, termino):
        """Busca libros por término utilizando el procedimiento almacenado"""
        self.db.connect()
        resultados = self.db.call_procedure("buscar_libros", (termino,))
        self.db.disconnect()
        return resultados
    
    def crear(self, libro):
        """Crea un nuevo libro"""
        self.db.connect()
        query = """
        INSERT INTO libros (titulo, subtitulo, isbn, fecha_publicacion, edicion, 
                           editorial, precio, stock, descripcion, num_paginas, 
                           idioma, imagen_portada, formato)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (libro.titulo, libro.subtitulo, libro.isbn, libro.fecha_publicacion,
                 libro.edicion, libro.editorial, libro.precio, libro.stock,
                 libro.descripcion, libro.num_paginas, libro.idioma,
                 libro.imagen_portada, libro.formato)
        
        result = self.db.execute_query(query, params)
        if result:
            # Obtener el ID del libro recién insertado
            libro_id = self.db.fetch_one("SELECT LAST_INSERT_ID() as id")['id']
            self.db.disconnect()
            return libro_id
        self.db.disconnect()
        return None
    
    def actualizar(self, libro):
        """Actualiza un libro existente"""
        self.db.connect()
        query = """
        UPDATE libros
        SET titulo = %s, subtitulo = %s, isbn = %s, fecha_publicacion = %s,
            edicion = %s, editorial = %s, precio = %s, stock = %s,
            descripcion = %s, num_paginas = %s, idioma = %s,
            imagen_portada = %s, formato = %s
        WHERE libro_id = %s
        """
        params = (libro.titulo, libro.subtitulo, libro.isbn, libro.fecha_publicacion,
                 libro.edicion, libro.editorial, libro.precio, libro.stock,
                 libro.descripcion, libro.num_paginas, libro.idioma,
                 libro.imagen_portada, libro.formato, libro.libro_id)
        
        result = self.db.execute_query(query, params)
        self.db.disconnect()
        return result
    
    def eliminar(self, libro_id):
        """Elimina un libro por su ID"""
        self.db.connect()
        result = self.db.execute_query("DELETE FROM libros WHERE libro_id = %s", (libro_id,))
        self.db.disconnect()
        return result
    
    def actualizar_stock(self, libro_id, cantidad):
        """Actualiza el stock de un libro utilizando el procedimiento almacenado"""
        self.db.connect()
        self.db.call_procedure("actualizar_stock", (libro_id, cantidad))
        self.db.disconnect()
    
    def asignar_autor(self, libro_id, autor_id):
        """Asigna un autor a un libro"""
        self.db.connect()
        result = self.db.execute_query(
            "INSERT INTO libro_autor (libro_id, autor_id) VALUES (%s, %s)",
            (libro_id, autor_id)
        )
        self.db.disconnect()
        return result
    
    def asignar_categoria(self, libro_id, categoria_id):
        """Asigna una categoría a un libro"""
        self.db.connect()
        result = self.db.execute_query(
            "INSERT INTO libro_categoria (libro_id, categoria_id) VALUES (%s, %s)",
            (libro_id, categoria_id)
        )
        self.db.disconnect()
        return result


class AutorController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def obtener_todos(self):
        """Obtiene todos los autores"""
        self.db.connect()
        autores = self.db.fetch_all("SELECT * FROM autores")
        self.db.disconnect()
        return autores
    
    def obtener_por_id(self, autor_id):
        """Obtiene un autor por su ID"""
        self.db.connect()
        autor = self.db.fetch_one("SELECT * FROM autores WHERE autor_id = %s", (autor_id,))
        self.db.disconnect()
        return autor
    
    def crear(self, autor):
        """Crea un nuevo autor"""
        self.db.connect()
        query = """
        INSERT INTO autores (nombre, apellido, fecha_nacimiento, fecha_fallecimiento, 
                           nacionalidad, sitio_web)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (autor.nombre, autor.apellido, autor.fecha_nacimiento,
                 autor.fecha_fallecimiento, autor.nacionalidad, autor.sitio_web)
        
        result = self.db.execute_query(query, params)
        if result:
            autor_id = self.db.fetch_one("SELECT LAST_INSERT_ID() as id")['id']
            self.db.disconnect()
            return autor_id
        self.db.disconnect()
        return None
    
    def actualizar(self, autor):
        """Actualiza un autor existente"""
        self.db.connect()
        query = """
        UPDATE autores
        SET nombre = %s, apellido = %s, fecha_nacimiento = %s,
            fecha_fallecimiento = %s, nacionalidad = %s, sitio_web = %s
        WHERE autor_id = %s
        """
        params = (autor.nombre, autor.apellido, autor.fecha_nacimiento,
                 autor.fecha_fallecimiento, autor.nacionalidad, 
                 autor.sitio_web, autor.autor_id)
        
        result = self.db.execute_query(query, params)
        self.db.disconnect()
        return result
    
    def eliminar(self, autor_id):
        """Elimina un autor por su ID"""
        self.db.connect()
        result = self.db.execute_query("DELETE FROM autores WHERE autor_id = %s", (autor_id,))
        self.db.disconnect()
        return result


class CategoriaController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def obtener_todas(self):
        """Obtiene todas las categorías"""
        self.db.connect()
        categorias = self.db.fetch_all("SELECT * FROM categorias")
        self.db.disconnect()
        return categorias
    
    def obtener_por_id(self, categoria_id):
        """Obtiene una categoría por su ID"""
        self.db.connect()
        categoria = self.db.fetch_one("SELECT * FROM categorias WHERE categoria_id = %s", (categoria_id,))
        self.db.disconnect()
        return categoria
    
    def crear(self, categoria):
        """Crea una nueva categoría"""
        self.db.connect()
        query = "INSERT INTO categorias (nombre, categoria_padre_id) VALUES (%s, %s)"
        params = (categoria.nombre, categoria.categoria_padre_id)
        
        result = self.db.execute_query(query, params)
        if result:
            categoria_id = self.db.fetch_one("SELECT LAST_INSERT_ID() as id")['id']
            self.db.disconnect()
            return categoria_id
        self.db.disconnect()
        return None
    
    def actualizar(self, categoria):
        """Actualiza una categoría existente"""
        self.db.connect()
        query = "UPDATE categorias SET nombre = %s, categoria_padre_id = %s WHERE categoria_id = %s"
        params = (categoria.nombre, categoria.categoria_padre_id, categoria.categoria_id)
        
        result = self.db.execute_query(query, params)
        self.db.disconnect()
        return result
    
    def eliminar(self, categoria_id):
        """Elimina una categoría por su ID"""
        self.db.connect()
        result = self.db.execute_query("DELETE FROM categorias WHERE categoria_id = %s", (categoria_id,))
        self.db.disconnect()
        return result


class ClienteController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def obtener_todos(self):
        """Obtiene todos los clientes"""
        self.db.connect()
        clientes = self.db.fetch_all("SELECT * FROM clientes")
        self.db.disconnect()
        return clientes
    
    def obtener_por_id(self, cliente_id):
        """Obtiene un cliente por su ID"""
        self.db.connect()
        cliente = self.db.fetch_one("SELECT * FROM clientes WHERE cliente_id = %s", (cliente_id,))
        self.db.disconnect()
        return cliente
    
    def crear(self, cliente):
        """Crea un nuevo cliente"""
        self.db.connect()
        query = """
        INSERT INTO clientes (nombre, apellido, email, telefono, direccion, 
                            ciudad, codigo_postal, pais)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (cliente.nombre, cliente.apellido, cliente.email, cliente.telefono,
                 cliente.direccion, cliente.ciudad, cliente.codigo_postal, cliente.pais)
        
        result = self.db.execute_query(query, params)
        if result:
            cliente_id = self.db.fetch_one("SELECT LAST_INSERT_ID() as id")['id']
            self.db.disconnect()
            return cliente_id
        self.db.disconnect()
        return None
    
    def actualizar(self, cliente):
        """Actualiza un cliente existente"""
        self.db.connect()
        query = """
        UPDATE clientes
        SET nombre = %s, apellido = %s, email = %s, telefono = %s,
            direccion = %s, ciudad = %s, codigo_postal = %s, pais = %s
        WHERE cliente_id = %s
        """
        params = (cliente.nombre, cliente.apellido, cliente.email, cliente.telefono,
                 cliente.direccion, cliente.ciudad, cliente.codigo_postal, 
                 cliente.pais, cliente.cliente_id)
        
        result = self.db.execute_query(query, params)
        self.db.disconnect()
        return result
    
    def eliminar(self, cliente_id):
        """Elimina un cliente por su ID"""
        self.db.connect()
        result = self.db.execute_query("DELETE FROM clientes WHERE cliente_id = %s", (cliente_id,))
        self.db.disconnect()
        return result


class VentaController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def obtener_todas(self):
        """Obtiene todas las ventas con sus detalles"""
        self.db.connect()
        ventas = self.db.fetch_all("SELECT * FROM vista_ventas_detallada")
        self.db.disconnect()
        return ventas
    
    def obtener_por_id(self, venta_id):
        """Obtiene una venta por su ID"""
        self.db.connect()
        venta = self.db.fetch_one("SELECT * FROM vista_ventas_detallada WHERE venta_id = %s", (venta_id,))
        self.db.disconnect()
        return venta
    
    def crear_venta(self, venta, detalles):
        """Crea una nueva venta con sus detalles"""
        self.db.connect()
        
        # Insertar la venta
        query_venta = """
        INSERT INTO ventas (cliente_id, total, metodo_pago, estado)
        VALUES (%s, %s, %s, %s)
        """
        params_venta = (venta.cliente_id, venta.total, venta.metodo_pago, venta.estado)
        
        result = self.db.execute_query(query_venta, params_venta)
        if not result:
            self.db.disconnect()
            return None
        
        # Obtener el ID de la venta recién insertada
        venta_id = self.db.fetch_one("SELECT LAST_INSERT_ID() as id")['id']
        
        # Insertar los detalles de la venta
        for detalle in detalles:
            query_detalle = """
            INSERT INTO detalles_venta (venta_id, libro_id, cantidad, precio_unitario, descuento)
            VALUES (%s, %s, %s, %s, %s)
            """
            params_detalle = (venta_id, detalle.libro_id, detalle.cantidad, 
                             detalle.precio_unitario, detalle.descuento)
            
            self.db.execute_query(query_detalle, params_detalle)
        
        self.db.disconnect()
        return venta_id
    
    def obtener_detalles_venta(self, venta_id):
        """Obtiene los detalles de una venta"""
        self.db.connect()
        query = """
        SELECT dv.*, l.titulo
        FROM detalles_venta dv
        JOIN libros l ON dv.libro_id = l.libro_id
        WHERE dv.venta_id = %s
        """
        detalles = self.db.fetch_all(query, (venta_id,))
        self.db.disconnect()
        return detalles


class ResenaController:
    def __init__(self):
        self.db = DatabaseManager()
    
    def obtener_por_libro(self, libro_id):
        """Obtiene todas las reseñas de un libro"""
        self.db.connect()
        query = """
        SELECT r.*, CONCAT(c.nombre, ' ', c.apellido) as cliente_nombre
        FROM resenas r
        JOIN clientes c ON r.cliente_id = c.cliente_id
        WHERE r.libro_id = %s
        ORDER BY r.fecha_resena DESC
        """
        resenas = self.db.fetch_all(query, (libro_id,))
        self.db.disconnect()
        return resenas
    
    def crear(self, resena):
        """Crea una nueva reseña"""
        self.db.connect()
        query = """
        INSERT INTO resenas (libro_id, cliente_id, calificacion, comentario)
        VALUES (%s, %s, %s, %s)
        """
        params = (resena.libro_id, resena.cliente_id, resena.calificacion, resena.comentario)
        
        result = self.db.execute_query(query, params)
        if result:
            resena_id = self.db.fetch_one("SELECT LAST_INSERT_ID() as id")['id']
            self.db.disconnect()
            return resena_id
        self.db.disconnect()
        return None