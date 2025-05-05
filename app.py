#!/usr/bin/env python3
"""
app.py – Sistema para trabajar con la base de datos de librería.

Uso:
  python app.py --host 127.0.0.1 --port 3306 --user root --password admin --database libreria
"""

import argparse
import mysql.connector
import sys
import logging
from tabulate import tabulate
from typing import List, Dict, Any, Optional, Tuple

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class SistemaLibreria:
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None
        self.conectar()

    def conectar(self):
        """Establece conexión con la base de datos."""
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=True
            )
            logging.info("Conexión a MySQL establecida correctamente")
        except mysql.connector.Error as err:
            logging.error(f"Error al conectar a MySQL: {err}")
            sys.exit(1)

    def cerrar(self):
        """Cierra la conexión con la base de datos."""
        if self.conn:
            self.conn.close()
            logging.info("Conexión a MySQL cerrada")

    def ejecutar_consulta(self, query: str, params: tuple = None) -> List[Dict]:
        """Ejecuta una consulta SQL y devuelve los resultados como una lista de diccionarios."""
        if not self.conn:
            self.conectar()
            
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            return resultados
        except mysql.connector.Error as err:
            logging.error(f"Error al ejecutar consulta: {err}")
            return []
        finally:
            cursor.close()

    def ejecutar_accion(self, query: str, params: tuple = None) -> int:
        """Ejecuta una acción SQL (INSERT, UPDATE, DELETE) y devuelve el número de filas afectadas."""
        if not self.conn:
            self.conectar()
            
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.rowcount
        except mysql.connector.Error as err:
            logging.error(f"Error al ejecutar acción: {err}")
            self.conn.rollback()
            return 0
        finally:
            cursor.close()

    def obtener_libros(self, filtro: str = None) -> List[Dict]:
        """Obtiene la lista de libros, opcionalmente filtrada por título, autor o categoría."""
        query = """
        SELECT l.libro_id, l.titulo, l.subtitulo, l.isbn, l.fecha_publicacion, 
               l.editorial, l.precio, l.stock, l.calificacion, l.formato,
               GROUP_CONCAT(DISTINCT CONCAT(a.nombre, ' ', a.apellido) SEPARATOR ', ') AS autores,
               GROUP_CONCAT(DISTINCT c.nombre SEPARATOR ', ') AS categorias
        FROM libros l
        LEFT JOIN libro_autor la ON l.libro_id = la.libro_id
        LEFT JOIN autores a ON la.autor_id = a.autor_id
        LEFT JOIN libro_categoria lc ON l.libro_id = lc.libro_id
        LEFT JOIN categorias c ON lc.categoria_id = c.categoria_id
        """
        
        params = ()
        if filtro:
            query += """
            WHERE l.titulo LIKE %s 
            OR CONCAT(a.nombre, ' ', a.apellido) LIKE %s
            OR c.nombre LIKE %s
            """
            params = (f"%{filtro}%", f"%{filtro}%", f"%{filtro}%")
            
        query += """
        GROUP BY l.libro_id
        ORDER BY l.titulo
        """
        
        return self.ejecutar_consulta(query, params)

    def obtener_libro_por_id(self, libro_id: int) -> Optional[Dict]:
        """Obtiene los detalles completos de un libro por su ID."""
        query = """
        SELECT l.*, 
               GROUP_CONCAT(DISTINCT CONCAT(a.nombre, ' ', a.apellido) SEPARATOR ', ') AS autores,
               GROUP_CONCAT(DISTINCT c.nombre SEPARATOR ', ') AS categorias
        FROM libros l
        LEFT JOIN libro_autor la ON l.libro_id = la.libro_id
        LEFT JOIN autores a ON la.autor_id = a.autor_id
        LEFT JOIN libro_categoria lc ON l.libro_id = lc.libro_id
        LEFT JOIN categorias c ON lc.categoria_id = c.categoria_id
        WHERE l.libro_id = %s
        GROUP BY l.libro_id
        """
        
        resultados = self.ejecutar_consulta(query, (libro_id,))
        return resultados[0] if resultados else None

    def obtener_autores(self) -> List[Dict]:
        """Obtiene la lista de autores con el número de libros que han escrito."""
        query = """
        SELECT a.autor_id, a.nombre, a.apellido, 
               COUNT(la.libro_id) AS num_libros
        FROM autores a
        LEFT JOIN libro_autor la ON a.autor_id = la.autor_id
        GROUP BY a.autor_id
        ORDER BY a.apellido, a.nombre
        """
        
        return self.ejecutar_consulta(query)
    
    def importar_libros_desde_google(self) -> bool:
        """Ejecuta el script de importar libros desde Google API."""
        try:
            from import_books import ImportadorLibros
            
            importador = ImportadorLibros(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                
            )
            
            logging.info("Ejecutando el script de importación de libros desde Google API...")
            libros = importador.obtener_libros()
            
            Importador.conectar()
            importador.insertar_libros(libros)
            importador.cerrar()
            
            logging.info("Libros importados correctamente.")
            return True
        except Exception as e:
            logging.error(f"Error al importar libros desde Google API: {e}")
            return False

    def obtener_categorias(self) -> List[Dict]:
        """Obtiene la lista de categorías con el número de libros en cada una."""
        query = """
        SELECT c.categoria_id, c.nombre, 
               COUNT(lc.libro_id) AS num_libros
        FROM categorias c
        LEFT JOIN libro_categoria lc ON c.categoria_id = lc.categoria_id
        GROUP BY c.categoria_id
        ORDER BY c.nombre
        """
        
        return self.ejecutar_consulta(query)

    def agregar_libro(self, datos_libro: Dict) -> int:
        """Agrega un nuevo libro a la base de datos."""
        # Insertar libro
        query_libro = """
        INSERT INTO libros (titulo, subtitulo, isbn, fecha_publicacion, edicion, 
                           editorial, precio, stock, descripcion, num_paginas, 
                           idioma, calificacion, imagen_portada, formato)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params_libro = (
            datos_libro.get('titulo', ''),
            datos_libro.get('subtitulo', ''),
            datos_libro.get('isbn', ''),
            datos_libro.get('fecha_publicacion'),
            datos_libro.get('edicion', '1ª Edición'),
            datos_libro.get('editorial', ''),
            float(datos_libro.get('precio', 0)),
            int(datos_libro.get('stock', 0)),
            datos_libro.get('descripcion', ''),
            int(datos_libro.get('num_paginas', 0)) if datos_libro.get('num_paginas') else None,
            datos_libro.get('idioma', 'es'),
            float(datos_libro.get('calificacion', 3.0)),
            datos_libro.get('imagen_portada', ''),
            datos_libro.get('formato', 'Tapa blanda')
        )
        
        self.ejecutar_accion(query_libro, params_libro)
        
        # Obtener ID del libro insertado
        libro_id = self.ejecutar_consulta("SELECT LAST_INSERT_ID() as id")[0]['id']
        
        # Procesar autores
        if 'autores' in datos_libro and datos_libro['autores']:
            for autor in datos_libro['autores']:
                # Verificar si el autor ya existe
                autor_id = self._obtener_o_crear_autor(autor)
                
                # Relacionar libro con autor
                self.ejecutar_accion(
                    "INSERT INTO libro_autor (libro_id, autor_id) VALUES (%s, %s)",
                    (libro_id, autor_id)
                )
        
        # Procesar categorías
        if 'categorias' in datos_libro and datos_libro['categorias']:
            for categoria in datos_libro['categorias']:
                # Verificar si la categoría ya existe
                categoria_id = self._obtener_o_crear_categoria(categoria)
                
                # Relacionar libro con categoría
                self.ejecutar_accion(
                    "INSERT INTO libro_categoria (libro_id, categoria_id) VALUES (%s, %s)",
                    (libro_id, categoria_id)
                )
        
        return libro_id

    def _obtener_o_crear_autor(self, autor: Dict) -> int:
        """Obtiene el ID de un autor o lo crea si no existe."""
        nombre = autor.get('nombre', '')
        apellido = autor.get('apellido', '')
        
        # Buscar autor
        query_buscar = "SELECT autor_id FROM autores WHERE nombre = %s AND apellido = %s"
        resultados = self.ejecutar_consulta(query_buscar, (nombre, apellido))
        
        if resultados:
            return resultados[0]['autor_id']
        
        # Crear autor
        query_crear = """
        INSERT INTO autores (nombre, apellido, fecha_nacimiento, fecha_fallecimiento, nacionalidad, sitio_web)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        self.ejecutar_accion(query_crear, (
            nombre,
            apellido,
            None,  # fecha_nacimiento
            None,  # fecha_fallecimiento
            None,  # nacionalidad
            None   # sitio_web
        ))
        
        return self.ejecutar_consulta("SELECT LAST_INSERT_ID() as id")[0]['id']

    def _obtener_o_crear_categoria(self, nombre_categoria: str) -> int:
        """Obtiene el ID de una categoría o la crea si no existe."""
        # Buscar categoría
        query_buscar = "SELECT categoria_id FROM categorias WHERE nombre = %s"
        resultados = self.ejecutar_consulta(query_buscar, (nombre_categoria,))
        
        if resultados:
            return resultados[0]['categoria_id']
        
        # Crear categoría
        query_crear = "INSERT INTO categorias (nombre, categoria_padre_id) VALUES (%s, %s)"
        self.ejecutar_accion(query_crear, (nombre_categoria, None))
        
        return self.ejecutar_consulta("SELECT LAST_INSERT_ID() as id")[0]['id']

    def actualizar_libro(self, libro_id: int, datos_libro: Dict) -> bool:
        """Actualiza los datos de un libro existente."""
        # Construir query dinámica para actualizar solo los campos proporcionados
        campos = []
        valores = []
        
        for campo, valor in datos_libro.items():
            if campo in ['titulo', 'subtitulo', 'isbn', 'fecha_publicacion', 'edicion', 
                        'editorial', 'precio', 'stock', 'descripcion', 'num_paginas', 
                        'idioma', 'calificacion', 'imagen_portada', 'formato']:
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        if not campos:
            return False
            
        query = f"UPDATE libros SET {', '.join(campos)} WHERE libro_id = %s"
        valores.append(libro_id)
        
        filas_afectadas = self.ejecutar_accion(query, tuple(valores))
        return filas_afectadas > 0

    def eliminar_libro(self, libro_id: int) -> bool:
        """Elimina un libro y sus relaciones."""
        # Eliminar relaciones
        self.ejecutar_accion("DELETE FROM libro_autor WHERE libro_id = %s", (libro_id,))
        self.ejecutar_accion("DELETE FROM libro_categoria WHERE libro_id = %s", (libro_id,))
        
        # Eliminar libro
        filas_afectadas = self.ejecutar_accion("DELETE FROM libros WHERE libro_id = %s", (libro_id,))
        return filas_afectadas > 0

    def buscar_libros(self, termino: str) -> List[Dict]:
        """Busca libros por título, autor, editorial o categoría."""
        query = """
        SELECT l.libro_id, l.titulo, l.subtitulo, l.isbn, 
               GROUP_CONCAT(DISTINCT CONCAT(a.nombre, ' ', a.apellido) SEPARATOR ', ') AS autores,
               l.editorial, l.precio, l.stock
        FROM libros l
        LEFT JOIN libro_autor la ON l.libro_id = la.libro_id
        LEFT JOIN autores a ON la.autor_id = a.autor_id
        LEFT JOIN libro_categoria lc ON l.libro_id = lc.libro_id
        LEFT JOIN categorias c ON lc.categoria_id = c.categoria_id
        WHERE l.titulo LIKE %s 
           OR l.subtitulo LIKE %s
           OR l.editorial LIKE %s
           OR CONCAT(a.nombre, ' ', a.apellido) LIKE %s
           OR c.nombre LIKE %s
        GROUP BY l.libro_id
        ORDER BY l.titulo
        """
        
        termino_busqueda = f"%{termino}%"
        params = (termino_busqueda, termino_busqueda, termino_busqueda, termino_busqueda, termino_busqueda)
        
        return self.ejecutar_consulta(query, params)

    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas generales de la librería."""
        estadisticas = {}
        
        # Total de libros
        query_total = "SELECT COUNT(*) as total FROM libros"
        resultado = self.ejecutar_consulta(query_total)
        estadisticas['total_libros'] = resultado[0]['total'] if resultado else 0
        
        # Valor del inventario
        query_valor = "SELECT SUM(precio * stock) as valor FROM libros"
        resultado = self.ejecutar_consulta(query_valor)
        estadisticas['valor_inventario'] = resultado[0]['valor'] if resultado and resultado[0]['valor'] else 0
        
        # Libros por categoría
        query_categorias = """
        SELECT c.nombre, COUNT(lc.libro_id) as cantidad
        FROM categorias c
        JOIN libro_categoria lc ON c.categoria_id = lc.categoria_id
        GROUP BY c.categoria_id
        ORDER BY cantidad DESC
        LIMIT 5
        """
        estadisticas['libros_por_categoria'] = self.ejecutar_consulta(query_categorias)
        
        # Autores con más libros
        query_autores = """
        SELECT CONCAT(a.nombre, ' ', a.apellido) as autor, COUNT(la.libro_id) as cantidad
        FROM autores a
        JOIN libro_autor la ON a.autor_id = la.autor_id
        GROUP BY a.autor_id
        ORDER BY cantidad DESC
        LIMIT 5
        """
        estadisticas['autores_top'] = self.ejecutar_consulta(query_autores)
        
        return estadisticas
        
    # Métodos para gestión de clientes
    def obtener_clientes(self) -> List[Dict]:
        """Obtiene la lista de todos los clientes."""
        query = """
        SELECT cliente_id, nombre, apellido, email, telefono, ciudad, pais
        FROM clientes
        ORDER BY apellido, nombre
        """
        return self.ejecutar_consulta(query)
    
    def obtener_cliente_por_id(self, cliente_id: int) -> Optional[Dict]:
        """Obtiene los detalles de un cliente por su ID."""
        query = "SELECT * FROM clientes WHERE cliente_id = %s"
        resultados = self.ejecutar_consulta(query, (cliente_id,))
        return resultados[0] if resultados else None
    
    def buscar_clientes(self, termino: str) -> List[Dict]:
        """Busca clientes por nombre, apellido o email."""
        query = """
        SELECT cliente_id, nombre, apellido, email, telefono, ciudad
        FROM clientes
        WHERE nombre LIKE %s OR apellido LIKE %s OR email LIKE %s
        ORDER BY apellido, nombre
        """
        termino_busqueda = f"%{termino}%"
        params = (termino_busqueda, termino_busqueda, termino_busqueda)
        return self.ejecutar_consulta(query, params)
    
    def agregar_cliente(self, datos_cliente: Dict) -> int:
        """Agrega un nuevo cliente a la base de datos."""
        query = """
        INSERT INTO clientes (nombre, apellido, email, telefono, direccion, ciudad, codigo_postal, pais)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            datos_cliente.get('nombre', ''),
            datos_cliente.get('apellido', ''),
            datos_cliente.get('email', ''),
            datos_cliente.get('telefono', ''),
            datos_cliente.get('direccion', ''),
            datos_cliente.get('ciudad', ''),
            datos_cliente.get('codigo_postal', ''),
            datos_cliente.get('pais', 'España')
        )
        self.ejecutar_accion(query, params)
        return self.ejecutar_consulta("SELECT LAST_INSERT_ID() as id")[0]['id']
    
    def actualizar_cliente(self, cliente_id: int, datos_cliente: Dict) -> bool:
        """Actualiza los datos de un cliente existente."""
        campos = []
        valores = []
        
        for campo, valor in datos_cliente.items():
            if campo in ['nombre', 'apellido', 'email', 'telefono', 'direccion', 'ciudad', 'codigo_postal', 'pais']:
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        if not campos:
            return False
            
        query = f"UPDATE clientes SET {', '.join(campos)} WHERE cliente_id = %s"
        valores.append(cliente_id)
        
        filas_afectadas = self.ejecutar_accion(query, tuple(valores))
        return filas_afectadas > 0
    
    def eliminar_cliente(self, cliente_id: int) -> bool:
        """Elimina un cliente de la base de datos."""
        filas_afectadas = self.ejecutar_accion("DELETE FROM clientes WHERE cliente_id = %s", (cliente_id,))
        return filas_afectadas > 0
    
    # Métodos para gestión de ventas
    def obtener_ventas(self) -> List[Dict]:
        """Obtiene la lista de todas las ventas."""
        query = """
        SELECT v.venta_id, v.fecha_venta, v.total, v.metodo_pago, v.estado,
               CONCAT(c.nombre, ' ', c.apellido) AS cliente
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.cliente_id
        ORDER BY v.fecha_venta DESC
        """
        return self.ejecutar_consulta(query)
    
    def obtener_venta_por_id(self, venta_id: int) -> Optional[Dict]:
        """Obtiene los detalles de una venta por su ID."""
        # Obtener datos de la venta
        query_venta = """
        SELECT v.*, CONCAT(c.nombre, ' ', c.apellido) AS cliente_nombre
        FROM ventas v
        JOIN clientes c ON v.cliente_id = c.cliente_id
        WHERE v.venta_id = %s
        """
        venta = self.ejecutar_consulta(query_venta, (venta_id,))
        
        if not venta:
            return None
            
        resultado = venta[0]
        
        # Obtener detalles de la venta
        query_detalles = """
        SELECT dv.*, l.titulo, l.isbn
        FROM detalles_venta dv
        JOIN libros l ON dv.libro_id = l.libro_id
        WHERE dv.venta_id = %s
        """
        detalles = self.ejecutar_consulta(query_detalles, (venta_id,))
        resultado['detalles'] = detalles
        
        return resultado
    
    def crear_venta(self, datos_venta: Dict) -> int:
        """Crea una nueva venta con sus detalles."""
        # Insertar venta
        query_venta = """
        INSERT INTO ventas (cliente_id, total, metodo_pago, estado)
        VALUES (%s, %s, %s, %s)
        """
        params_venta = (
            datos_venta.get('cliente_id'),
            datos_venta.get('total', 0),
            datos_venta.get('metodo_pago', 'Efectivo'),
            datos_venta.get('estado', 'Completada')
        )
        self.ejecutar_accion(query_venta, params_venta)
        venta_id = self.ejecutar_consulta("SELECT LAST_INSERT_ID() as id")[0]['id']
        
        # Insertar detalles de venta
        if 'detalles' in datos_venta and datos_venta['detalles']:
            for detalle in datos_venta['detalles']:
                query_detalle = """
                INSERT INTO detalles_venta (venta_id, libro_id, cantidad, precio_unitario, descuento)
                VALUES (%s, %s, %s, %s, %s)
                """
                params_detalle = (
                    venta_id,
                    detalle.get('libro_id'),
                    detalle.get('cantidad', 1),
                    detalle.get('precio_unitario'),
                    detalle.get('descuento', 0)
                )
                self.ejecutar_accion(query_detalle, params_detalle)
                
                # El trigger after_venta_insert se encargará de actualizar el stock
        
        return venta_id

    def mostrar_tabla(self, datos: List[Dict], titulo: str = None):
        """Muestra una tabla formateada con los datos proporcionados."""
        if not datos:
            print("No hay datos para mostrar.")
            return
            
        if titulo:
            print(f"\n=== {titulo} ===")
            
        # Obtener encabezados de las columnas
        headers = list(datos[0].keys())
        
        # Crear tabla
        tabla = [[fila[col] for col in headers] for fila in datos]
        
        # Mostrar tabla
        print(tabulate(tabla, headers=headers, tablefmt="grid"))

def menu_principal():
    """Muestra el menú principal del sistema."""
    print("\n=== SISTEMA DE GESTIÓN DE LIBRERÍA ===")
    print("1. Gestionar Libros")
    print("2. Gestionar Autores")
    print("3. Gestionar Categorías")
    print("4. Gestionar Clientes")
    print("5. Gestionar Ventas")
    print("6. Buscar")
    print("7. Estadísticas")
    print("0. Salir")
    return input("Seleccione una opción: ")

def menu_libros():
    """Muestra el menú de gestión de libros."""
    print("\n=== GESTIÓN DE LIBROS ===")
    print("1. Ver todos los libros")
    print("2. Ver detalles de un libro")
    print("3. Agregar nuevo libro")
    print("4. Actualizar libro")
    print("5. Eliminar libro")
    print("0. Volver al menú principal")
    return input("Seleccione una opción: ")

def menu_autores():
    """Muestra el menú de gestión de autores."""
    print("\n=== GESTIÓN DE AUTORES ===")
    print("1. Ver todos los autores")
    print("2. Ver libros de un autor")
    print("0. Volver al menú principal")
    return input("Seleccione una opción: ")

def menu_categorias():
    """Muestra el menú de gestión de categorías."""
    print("\n=== GESTIÓN DE CATEGORÍAS ===")
    print("1. Ver todas las categorías")
    print("2. Ver libros de una categoría")
    print("0. Volver al menú principal")
    return input("Seleccione una opción: ")

def menu_clientes():
    """Muestra el menú de gestión de clientes."""
    print("\n=== GESTIÓN DE CLIENTES ===")
    print("1. Ver todos los clientes")
    print("2. Ver detalles de un cliente")
    print("3. Agregar nuevo cliente")
    print("4. Actualizar cliente")
    print("5. Eliminar cliente")
    print("6. Buscar clientes")
    print("0. Volver al menú principal")
    return input("Seleccione una opción: ")

def menu_ventas():
    """Muestra el menú de gestión de ventas."""
    print("\n=== GESTIÓN DE VENTAS ===")
    print("1. Ver todas las ventas")
    print("2. Ver detalles de una venta")
    print("3. Crear nueva venta")
    print("0. Volver al menú principal")
    return input("Seleccione una opción: ")

def main():
    parser = argparse.ArgumentParser(description='Sistema de gestión de librería')
    parser.add_argument("--host", help="Host de la base de datos")
    parser.add_argument("--port", type=int, help="Puerto de MySQL")
    parser.add_argument("--user", help="Usuario de la base de datos")
    parser.add_argument("--password", help="Contraseña de la base de datos")
    parser.add_argument("--database", help="Nombre de la base de datos")
    args = parser.parse_args()
    
    # Importar configuración desde config.py
    try:
        from config import DB_CONFIG
        # Usar valores de línea de comandos si se proporcionan, de lo contrario usar config.py
        host = args.host if args.host else DB_CONFIG.get('host', 'localhost')
        user = args.user if args.user else DB_CONFIG.get('user', 'root')
        password = args.password if args.password else DB_CONFIG.get('password', '')
        database = args.database if args.database else DB_CONFIG.get('database', 'libreria')
        port = args.port if args.port else DB_CONFIG.get('port', 3306)
        
        logging.info("Usando configuración desde config.py")
    except ImportError:
        logging.warning("No se pudo importar config.py, usando valores por defecto o de línea de comandos")
        host = args.host if args.host else 'localhost'
        user = args.user
        password = args.password
        database = args.database if args.database else 'libreria'
        port = args.port if args.port else 3306
        
        if not user or not password:
            print("Error: Se requiere usuario y contraseña. Proporcione estos valores como argumentos o en config.py")
            sys.exit(1)
    
    sistema = SistemaLibreria(host, user, password, database, port)
    
    try:
        while True:
            opcion = menu_principal()
            
            if opcion == "1":  # Gestionar Libros
                gestionar_libros(sistema)
            elif opcion == "2":  # Gestionar Autores
                gestionar_autores(sistema)
            elif opcion == "3":  # Gestionar Categorías
                gestionar_categorias(sistema)
            elif opcion == "4":  # Gestionar Clientes
                gestionar_clientes(sistema)
            elif opcion == "5":  # Gestionar Ventas
                gestionar_ventas(sistema)
            elif opcion == "6":  # Buscar
                termino = input("\nIntroduzca término de búsqueda: ")
                resultados = sistema.buscar_libros(termino)
                sistema.mostrar_tabla(resultados, f"Resultados para '{termino}'")
            elif opcion == "7":  # Estadísticas
                mostrar_estadisticas(sistema)
            elif opcion == "0":  # Salir
                break
            else:
                print("Opción no válida. Intente de nuevo.")
    
    finally:
        sistema.cerrar()

def gestionar_libros(sistema: SistemaLibreria):
    """Gestiona las operaciones relacionadas con libros."""
    while True:
        opcion = menu_libros()
        
        if opcion == "1":  # Ver todos los libros
            libros = sistema.obtener_libros()
            sistema.mostrar_tabla(libros, "Catálogo de Libros")
        
        elif opcion == "2":  # Ver detalles de un libro
            libro_id = input("Introduzca ID del libro: ")
            try:
                libro = sistema.obtener_libro_por_id(int(libro_id))
                if libro:
                    print("\n=== DETALLES DEL LIBRO ===")
                    for campo, valor in libro.items():
                        print(f"{campo}: {valor}")
                else:
                    print(f"No se encontró libro con ID {libro_id}")
            except ValueError:
                print("ID de libro no válido")
        
        elif opcion == "3":  # Agregar nuevo libro
            datos_libro = {}
            datos_libro['titulo'] = input("Título: ")
            datos_libro['subtitulo'] = input("Subtítulo (opcional): ")
            datos_libro['isbn'] = input("ISBN: ")
            datos_libro['editorial'] = input("Editorial: ")
            
            try:
                datos_libro['precio'] = float(input("Precio: "))
                datos_libro['stock'] = int(input("Stock: "))
            except ValueError:
                print("Valores numéricos no válidos")
                continue
                
            datos_libro['fecha_publicacion'] = input("Fecha de publicación (YYYY-MM-DD): ")
            datos_libro['formato'] = input("Formato (Tapa blanda, Tapa dura, Ebook): ")
            datos_libro['descripcion'] = input("Descripción: ")
            
            # Autores
            autores = []
            while True:
                nombre = input("Nombre del autor (dejar vacío para terminar): ")
                if not nombre:
                    break
                apellido = input("Apellido del autor: ")
                autores.append({'nombre': nombre, 'apellido': apellido})
            datos_libro['autores'] = autores
            
            # Categorías
            categorias = []
            while True:
                categoria = input("Categoría (dejar vacío para terminar): ")
                if not categoria:
                    break
                categorias.append(categoria)
            datos_libro['categorias'] = categorias
            
            libro_id = sistema.agregar_libro(datos_libro)
            print(f"Libro agregado con ID: {libro_id}")
        
        elif opcion == "4":  # Actualizar libro
            libro_id = input("Introduzca ID del libro a actualizar: ")
            try:
                libro_id = int(libro_id)
                libro = sistema.obtener_libro_por_id(libro_id)
                if not libro:
                    print(f"No se encontró libro con ID {libro_id}")
                    continue
                    
                print("\nDeje en blanco los campos que no desea modificar:")
                datos_actualizados = {}
                
                titulo = input(f"Título [{libro['titulo']}]: ")
                if titulo:
                    datos_actualizados['titulo'] = titulo
                    
                subtitulo = input(f"Subtítulo [{libro['subtitulo']}]: ")
                if subtitulo:
                    datos_actualizados['subtitulo'] = subtitulo
                
                precio = input(f"Precio [{libro['precio']}]: ")
                if precio:
                    try:
                        datos_actualizados['precio'] = float(precio)
                    except ValueError:
                        print("Precio no válido")
                
                stock = input(f"Stock [{libro['stock']}]: ")
                if stock:
                    try:
                        datos_actualizados['stock'] = int(stock)
                    except ValueError:
                        print("Stock no válido")
                
                if datos_actualizados:
                    if sistema.actualizar_libro(libro_id, datos_actualizados):
                        print("Libro actualizado correctamente")
                    else:
                        print("No se pudo actualizar el libro")
                else:
                    print("No se realizaron cambios")
                    
            except ValueError:
                print("ID de libro no válido")
        
        elif opcion == "5":  # Eliminar libro
            libro_id = input("Introduzca ID del libro a eliminar: ")
            try:
                libro_id = int(libro_id)
                confirmacion = input(f"¿Está seguro de eliminar el libro con ID {libro_id}? (s/n): ")
                if confirmacion.lower() == 's':
                    if sistema.eliminar_libro(libro_id):
                        print("Libro eliminado correctamente")
                    else:
                        print("No se pudo eliminar el libro")
            except ValueError:
                print("ID de libro no válido")
        
        elif opcion == "0":  # Volver al menú principal
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

def gestionar_autores(sistema: SistemaLibreria):
    """Gestiona las operaciones relacionadas con autores."""
    while True:
        opcion = menu_autores()
        
        if opcion == "1":  # Ver todos los autores
            autores = sistema.obtener_autores()
            sistema.mostrar_tabla(autores, "Lista de Autores")
        
        elif opcion == "2":  # Ver libros de un autor
            autor_id = input("Introduzca ID del autor: ")
            try:
                autor_id = int(autor_id)
                # Obtener nombre del autor
                query = "SELECT CONCAT(nombre, ' ', apellido) as nombre FROM autores WHERE autor_id = %s"
                resultado = sistema.ejecutar_consulta(query, (autor_id,))
                
                if not resultado:
                    print(f"No se encontró autor con ID {autor_id}")
                    continue
                    
                nombre_autor = resultado[0]['nombre']
                
                # Obtener libros del autor
                query = """
                SELECT l.libro_id, l.titulo, l.subtitulo, l.editorial, l.precio
                FROM libros l
                JOIN libro_autor la ON l.libro_id = la.libro_id
                WHERE la.autor_id = %s
                ORDER BY l.titulo
                """
                
                libros = sistema.ejecutar_consulta(query, (autor_id,))
                sistema.mostrar_tabla(libros, f"Libros de {nombre_autor}")
                
            except ValueError:
                print("ID de autor no válido")
        
        elif opcion == "0":  # Volver al menú principal
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

def gestionar_categorias(sistema: SistemaLibreria):
    """Gestiona las operaciones relacionadas con categorías."""
    while True:
        opcion = menu_categorias()
        
        if opcion == "1":  # Ver todas las categorías
            categorias = sistema.obtener_categorias()
            sistema.mostrar_tabla(categorias, "Lista de Categorías")
        
        elif opcion == "2":  # Ver libros de una categoría
            categoria_id = input("Introduzca ID de la categoría: ")
            try:
                categoria_id = int(categoria_id)
                # Obtener nombre de la categoría
                query = "SELECT nombre FROM categorias WHERE categoria_id = %s"
                resultado = sistema.ejecutar_consulta(query, (categoria_id,))
                
                if not resultado:
                    print(f"No se encontró categoría con ID {categoria_id}")
                    continue
                    
                nombre_categoria = resultado[0]['nombre']
                
                # Obtener libros de la categoría
                query = """
                SELECT l.libro_id, l.titulo, l.subtitulo, 
                       GROUP_CONCAT(DISTINCT CONCAT(a.nombre, ' ', a.apellido) SEPARATOR ', ') AS autores,
                       l.editorial, l.precio
                FROM libros l
                JOIN libro_categoria lc ON l.libro_id = lc.libro_id
                LEFT JOIN libro_autor la ON l.libro_id = la.libro_id
                LEFT JOIN autores a ON la.autor_id = a.autor_id
                WHERE lc.categoria_id = %s
                GROUP BY l.libro_id
                ORDER BY l.titulo
                """
                
                libros = sistema.ejecutar_consulta(query, (categoria_id,))
                sistema.mostrar_tabla(libros, f"Libros de categoría: {nombre_categoria}")
                
            except ValueError:
                print("ID de categoría no válido")
        
        elif opcion == "0":  # Volver al menú principal
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

def mostrar_estadisticas(sistema: SistemaLibreria):
    """Muestra estadísticas generales de la librería."""
    estadisticas = sistema.obtener_estadisticas()
    
    print("\n=== ESTADÍSTICAS DE LA LIBRERÍA ===")
    print(f"Total de libros: {estadisticas['total_libros']}")
    print(f"Valor del inventario: ${estadisticas['valor_inventario']:.2f}")
    
    print("\nTop 5 Categorías:")
    sistema.mostrar_tabla(estadisticas['libros_por_categoria'])
    
    print("\nTop 5 Autores:")
    sistema.mostrar_tabla(estadisticas['autores_top'])

def gestionar_clientes(sistema: SistemaLibreria):
    """Gestiona las operaciones relacionadas con clientes."""
    while True:
        opcion = menu_clientes()
        
        if opcion == "1":  # Ver todos los clientes
            clientes = sistema.obtener_clientes()
            sistema.mostrar_tabla(clientes, "Lista de Clientes")
        
        elif opcion == "2":  # Ver detalles de un cliente
            cliente_id = input("Introduzca ID del cliente: ")
            try:
                cliente = sistema.obtener_cliente_por_id(int(cliente_id))
                if cliente:
                    print("\n=== DETALLES DEL CLIENTE ===")
                    for campo, valor in cliente.items():
                        print(f"{campo}: {valor}")
                else:
                    print(f"No se encontró cliente con ID {cliente_id}")
            except ValueError:
                print("ID de cliente no válido")
        
        elif opcion == "3":  # Agregar nuevo cliente
            datos_cliente = {}
            datos_cliente['nombre'] = input("Nombre: ")
            datos_cliente['apellido'] = input("Apellido: ")
            datos_cliente['email'] = input("Email: ")
            datos_cliente['telefono'] = input("Teléfono (opcional): ")
            datos_cliente['direccion'] = input("Dirección (opcional): ")
            datos_cliente['ciudad'] = input("Ciudad (opcional): ")
            datos_cliente['codigo_postal'] = input("Código Postal (opcional): ")
            datos_cliente['pais'] = input("País (opcional, por defecto 'España'): ") or "España"
            
            cliente_id = sistema.agregar_cliente(datos_cliente)
            print(f"Cliente agregado con ID: {cliente_id}")
        
        elif opcion == "4":  # Actualizar cliente
            cliente_id = input("Introduzca ID del cliente a actualizar: ")
            try:
                cliente_id = int(cliente_id)
                cliente = sistema.obtener_cliente_por_id(cliente_id)
                if not cliente:
                    print(f"No se encontró cliente con ID {cliente_id}")
                    continue
                    
                print("\nDeje en blanco los campos que no desea modificar:")
                datos_actualizados = {}
                
                nombre = input(f"Nombre [{cliente['nombre']}]: ")
                if nombre:
                    datos_actualizados['nombre'] = nombre
                    
                apellido = input(f"Apellido [{cliente['apellido']}]: ")
                if apellido:
                    datos_actualizados['apellido'] = apellido
                
                email = input(f"Email [{cliente['email']}]: ")
                if email:
                    datos_actualizados['email'] = email
                
                telefono = input(f"Teléfono [{cliente.get('telefono', '')}]: ")
                if telefono:
                    datos_actualizados['telefono'] = telefono
                
                direccion = input(f"Dirección [{cliente.get('direccion', '')}]: ")
                if direccion:
                    datos_actualizados['direccion'] = direccion
                
                ciudad = input(f"Ciudad [{cliente.get('ciudad', '')}]: ")
                if ciudad:
                    datos_actualizados['ciudad'] = ciudad
                
                if datos_actualizados:
                    if sistema.actualizar_cliente(cliente_id, datos_actualizados):
                        print("Cliente actualizado correctamente")
                    else:
                        print("No se pudo actualizar el cliente")
                else:
                    print("No se realizaron cambios")
                    
            except ValueError:
                print("ID de cliente no válido")
        
        elif opcion == "5":  # Eliminar cliente
            cliente_id = input("Introduzca ID del cliente a eliminar: ")
            try:
                cliente_id = int(cliente_id)
                confirmacion = input(f"¿Está seguro de eliminar el cliente con ID {cliente_id}? (s/n): ")
                if confirmacion.lower() == 's':
                    if sistema.eliminar_cliente(cliente_id):
                        print("Cliente eliminado correctamente")
                    else:
                        print("No se pudo eliminar el cliente")
            except ValueError:
                print("ID de cliente no válido")
        
        elif opcion == "6":  # Buscar clientes
            termino = input("Introduzca término de búsqueda: ")
            resultados = sistema.buscar_clientes(termino)
            sistema.mostrar_tabla(resultados, f"Resultados para '{termino}'")
        
        elif opcion == "0":  # Volver al menú principal
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

def gestionar_ventas(sistema: SistemaLibreria):
    """Gestiona las operaciones relacionadas con ventas."""
    while True:
        opcion = menu_ventas()
        
        if opcion == "1":  # Ver todas las ventas
            ventas = sistema.obtener_ventas()
            sistema.mostrar_tabla(ventas, "Lista de Ventas")
        
        elif opcion == "2":  # Ver detalles de una venta
            venta_id = input("Introduzca ID de la venta: ")
            try:
                venta = sistema.obtener_venta_por_id(int(venta_id))
                if venta:
                    print("\n=== DETALLES DE LA VENTA ===")
                    print(f"Venta ID: {venta['venta_id']}")
                    print(f"Cliente: {venta['cliente_nombre']}")
                    print(f"Fecha: {venta['fecha_venta']}")
                    print(f"Total: ${venta['total']:.2f}")
                    print(f"Método de pago: {venta['metodo_pago']}")
                    print(f"Estado: {venta['estado']}")
                    
                    print("\n=== PRODUCTOS VENDIDOS ===")
                    sistema.mostrar_tabla(venta['detalles'], "Detalles de la venta")
                else:
                    print(f"No se encontró venta con ID {venta_id}")
            except ValueError:
                print("ID de venta no válido")
        
        elif opcion == "3":  # Crear nueva venta
            # Seleccionar cliente
            cliente_id = input("Introduzca ID del cliente: ")
            try:
                cliente_id = int(cliente_id)
                cliente = sistema.obtener_cliente_por_id(cliente_id)
                if not cliente:
                    print(f"No se encontró cliente con ID {cliente_id}")
                    continue
                    
                print(f"Cliente seleccionado: {cliente['nombre']} {cliente['apellido']}")
                
                # Agregar productos a la venta
                detalles = []
                total_venta = 0
                
                while True:
                    libro_id = input("\nIntroduzca ID del libro (0 para terminar): ")
                    if libro_id == "0":
                        break
                        
                    try:
                        libro_id = int(libro_id)
                        libro = sistema.obtener_libro_por_id(libro_id)
                        if not libro:
                            print(f"No se encontró libro con ID {libro_id}")
                            continue
                            
                        print(f"Libro: {libro['titulo']}")
                        print(f"Precio: ${libro['precio']:.2f}")
                        print(f"Stock disponible: {libro['stock']}")
                        
                        if libro['stock'] <= 0:
                            print("Este libro no tiene stock disponible")
                            continue
                            
                        cantidad = input("Cantidad: ")
                        try:
                            cantidad = int(cantidad)
                            if cantidad <= 0:
                                print("La cantidad debe ser mayor a 0")
                                continue
                                
                            if cantidad > libro['stock']:
                                print(f"No hay suficiente stock. Disponible: {libro['stock']}")
                                continue
                                
                            precio = libro['precio']
                            subtotal = precio * cantidad
                            
                            from decimal import Decimal
                            
                            descuento = input("Descuento % (0-100): ")
                            try:
                                descuento = float(descuento) if descuento else 0
                                if descuento < 0 or descuento > 100:
                                    print("El descuento debe estar entre 0 y 100")
                                    descuento = 0
                                    
                                descuento_decimal = descuento / 100
                                precio_con_descuento = precio * Decimal(1 - descuento_decimal)
                                subtotal = precio_con_descuento * cantidad
                                
                                detalles.append({
                                    'libro_id': libro_id,
                                    'cantidad': cantidad,
                                    'precio_unitario': precio,
                                    'descuento': descuento_decimal,
                                    'subtotal': subtotal,
                                    'titulo': libro['titulo']
                                })
                                
                                total_venta += subtotal
                                print(f"Producto agregado. Subtotal: ${subtotal:.2f}")
                                
                            except ValueError:
                                print("Descuento no válido")
                                
                        except ValueError:
                            print("Cantidad no válida")
                            
                    except ValueError:
                        print("ID de libro no válido")
                
                if not detalles:
                    print("No se agregaron productos a la venta")
                    continue
                    
                # Mostrar resumen de la venta
                print("\n=== RESUMEN DE LA VENTA ===")
                print(f"Cliente: {cliente['nombre']} {cliente['apellido']}")
                print(f"Total: ${total_venta:.2f}")
                
                # Mostrar detalles
                tabla_detalles = []
                for d in detalles:
                    tabla_detalles.append({
                        'Libro': d['titulo'],
                        'Cantidad': d['cantidad'],
                        'Precio': f"${d['precio_unitario']:.2f}",
                        'Descuento': f"{d['descuento']*100:.0f}%",
                        'Subtotal': f"${d['subtotal']:.2f}"
                    })
                sistema.mostrar_tabla(tabla_detalles, "Productos")
                
                # Confirmar venta
                confirmacion = input("\n¿Confirmar venta? (s/n): ")
                if confirmacion.lower() != 's':
                    print("Venta cancelada")
                    continue
                    
                # Método de pago
                metodo_pago = input("Método de pago (Efectivo, Tarjeta, Transferencia): ") or "Efectivo"
                
                # Crear venta
                datos_venta = {
                    'cliente_id': cliente_id,
                    'total': total_venta,
                    'metodo_pago': metodo_pago,
                    'detalles': detalles
                }
                
                venta_id = sistema.crear_venta(datos_venta)
                print(f"\nVenta creada con éxito. ID: {venta_id}")
                
            except ValueError:
                print("ID de cliente no válido")
        
        elif opcion == "0":  # Volver al menú principal
            break
        
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()