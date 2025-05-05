#!/usr/bin/env python3
"""
import_books.py – Carga el catálogo de libros a MySQL usando Google Books API.

Uso:
  python import_books.py --host 127.0.0.1 --port 3305 --user root \
        --password admin --database libreria
"""

import json, argparse, mysql.connector, sys, requests, time, random
from datetime import datetime
from typing import List, Dict, Any
import logging
from urllib.parse import quote
from config import DB_CONFIG

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_books.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ImportadorLibros:
    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.conn = None

    def obtener_libros(self) -> List[Dict[str, Any]]:
        try:
            # Lista de categorías populares para buscar
            categorias = [
                "subject:fiction",
                "subject:nonfiction",
                "subject:romance",
                "subject:mystery",
                "subject:science fiction",
                "subject:fantasy",
                "subject:biography",
                "subject:history",
                "subject:literature",
                "subject:poetry",
                "subject:programming",
                "subject:data science",
                "subject:artificial intelligence",
                "subject:business",
                "subject:self-help"
            ]
            
            todos_libros = []
            max_resultados = 40
            
            for categoria in categorias:
                try:
                    # Buscar en Google Books
                    categoria_codificada = quote(categoria)
                    gb_url = f"https://www.googleapis.com/books/v1/volumes?q={categoria_codificada}&maxResults={max_resultados}&langRestrict=es"
                    
                    logging.info(f"Buscando libros de categoría: {categoria.split(':')[1]}")
                    respuesta = requests.get(gb_url, timeout=20)
                    respuesta.raise_for_status()
                    
                    gb_data = respuesta.json()
                    
                    for item in gb_data.get('items', []):
                        # Obtener ISBN si está disponible
                        isbn = None
                        industry_ids = item.get('volumeInfo', {}).get('industryIdentifiers', [])
                        for id_type in industry_ids:
                            if id_type.get('type') == 'ISBN_13':
                                isbn = id_type.get('identifier')
                                break
                            elif id_type.get('type') == 'ISBN_10' and not isbn:
                                isbn = id_type.get('identifier')
                        
                        if not isbn:
                            # Generar ISBN ficticio si no existe
                            isbn = self._generar_isbn_falso()
                            
                        # Procesar libro directamente de Google Books
                        libro = self._procesar_libro(item)
                        if libro and not any(b['isbn'] == libro['isbn'] for b in todos_libros):
                            todos_libros.append(libro)
                    
                    time.sleep(1)  # Pausa entre peticiones
                    
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error al obtener libros de categoría {categoria}: {e}")
                    continue
                except json.JSONDecodeError:
                    logging.error(f"Error al decodificar respuesta JSON para categoría {categoria}")
                    continue
            
            logging.info(f"Total de libros únicos encontrados: {len(todos_libros)}")
            return todos_libros
            
        except Exception as e:
            logging.error(f"Error inesperado al obtener libros: {e}")
            sys.exit(1)

    def _generar_isbn_falso(self) -> str:
        """Genera un ISBN-13 ficticio pero válido"""
        # Prefijo de ISBN-13 para libros (978)
        prefijo = "978"
        
        # Generar 9 dígitos aleatorios
        medio = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        # Calcular dígito de verificación
        digitos = prefijo + medio
        digito_verificacion = self._calcular_digito_verificacion_isbn13(digitos)
        
        return digitos + digito_verificacion

    def _calcular_digito_verificacion_isbn13(self, digitos: str) -> str:
        """Calcula el dígito de verificación para un ISBN-13"""
        total = 0
        for i, digito in enumerate(digitos):
            if i % 2 == 0:
                total += int(digito)
            else:
                total += 3 * int(digito)
        
        check = (10 - (total % 10)) % 10
        return str(check)

    def _procesar_libro(self, gb_item: Dict[str, Any]) -> Dict[str, Any]:
        try:
            gb_info = gb_item.get('volumeInfo', {})
            
            # Obtener ISBN
            isbn = None
            industry_ids = gb_info.get('industryIdentifiers', [])
            for id_type in industry_ids:
                if id_type.get('type') == 'ISBN_13':
                    isbn = id_type.get('identifier')
                    break
                elif id_type.get('type') == 'ISBN_10' and not isbn:
                    isbn = id_type.get('identifier')
            
            if not isbn:
                isbn = self._generar_isbn_falso()
                
            # Procesar fecha de publicación
            fecha_publicacion = None
            if 'publishedDate' in gb_info:
                try:
                    fecha_publicacion = datetime.strptime(gb_info['publishedDate'], '%Y-%m-%d').strftime('%Y-%m-%d')
                except ValueError:
                    try:
                        fecha_publicacion = datetime.strptime(gb_info['publishedDate'], '%Y-%m').strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            fecha_publicacion = datetime.strptime(gb_info['publishedDate'], '%Y').strftime('%Y-%m-%d')
                        except:
                            # Generar fecha aleatoria entre 1950 y 2023
                            anio = random.randint(1950, 2023)
                            mes = random.randint(1, 12)
                            dia = random.randint(1, 28)
                            fecha_publicacion = f"{anio}-{mes:02d}-{dia:02d}"
            else:
                # Generar fecha aleatoria entre 1950 y 2023
                anio = random.randint(1950, 2023)
                mes = random.randint(1, 12)
                dia = random.randint(1, 28)
                fecha_publicacion = f"{anio}-{mes:02d}-{dia:02d}"
            
            # Obtener formato del libro
            formato = 'Tapa blanda'  # Por defecto
            if 'epub' in gb_item.get('accessInfo', {}).get('epub', {}):
                formato = 'Ebook'
            elif 'pdf' in gb_item.get('accessInfo', {}).get('pdf', {}):
                formato = 'Ebook'
            elif 'dimensions' in gb_info:
                formato = 'Tapa dura'
                
            # Obtener imagen de portada
            imagen_portada = None
            if 'imageLinks' in gb_info:
                for calidad in ['extraLarge', 'large', 'medium', 'small', 'thumbnail', 'smallThumbnail']:
                    if calidad in gb_info['imageLinks']:
                        imagen_portada = gb_info['imageLinks'][calidad]
                        break
                        
            # Generar precio basado en la popularidad
            precio_base = random.uniform(10, 50)
            if gb_info.get('averageRating'):
                precio_base *= (1 + (gb_info['averageRating'] - 3) * 0.1)
            precio = round(precio_base, 2)
            
            # Generar stock basado en la popularidad
            stock_base = random.randint(5, 20)
            if gb_info.get('ratingsCount', 0) > 100:
                stock_base += 5
            stock = stock_base
            
            # Calcular calificación basado en precio y páginas
            num_paginas = gb_info.get('pageCount', 0)
            if num_paginas > 0 and precio > 0:
                # Normalizar valores para calcular calificación
                paginas_normalizadas = min(num_paginas / 1000, 1)  # Máximo 1000 páginas
                precio_normalizado = min(precio / 50, 1)  # Máximo 50 euros
                
                # Calcular calificación (0-5) basado en valor por página
                valor_por_pagina = paginas_normalizadas / precio_normalizado
                calificacion = min(5, max(0, valor_por_pagina * 5))
            else:
                calificacion = 3.0  # Calificación por defecto
            
            # Procesar autores
            info_autores = []
            for autor in gb_info.get('authors', ['Autor Desconocido']):
                # Dividir nombre del autor
                partes = autor.split()
                if len(partes) == 1:
                    nombre = partes[0]
                    apellido = ''
                else:
                    nombre = partes[0]
                    apellido = ' '.join(partes[1:])
                
                info_autores.append({
                    'nombre': nombre,
                    'apellido': apellido,
                    'nombre_completo': autor
                })
            
            # Procesar categorías
            categorias = []
            if 'categories' in gb_info:
                categorias.extend(gb_info['categories'])
            if not categorias:
                # Extraer categoría de la consulta original
                if 'subject' in gb_item.get('selfLink', ''):
                    tema = gb_item['selfLink'].split('subject:')[1].split('&')[0]
                    categorias = [tema.capitalize()]
                else:
                    categorias = ['General']
            
            # Obtener descripción
            descripcion = gb_info.get('description', '')
            if not descripcion:
                # Generar descripción genérica
                descripcion = f"Este libro de {categorias[0] if categorias else 'temática general'} escrito por {info_autores[0]['nombre_completo'] if info_autores else 'un autor desconocido'} explora diversos temas relevantes en su campo."
            
            # Generar subtítulo si no existe
            subtitulo = gb_info.get('subtitle', '')
            if not subtitulo and random.random() < 0.3:  # 30% de probabilidad de tener subtítulo
                plantillas_subtitulos = [
                    f"Una introducción a {categorias[0] if categorias else 'la materia'}",
                    f"Perspectivas modernas sobre {categorias[0] if categorias else 'el tema'}",
                    f"Guía práctica de {categorias[0] if categorias else 'la disciplina'}",
                    f"Teoría y práctica en {categorias[0] if categorias else 'el campo'}",
                    f"Conceptos avanzados de {categorias[0] if categorias else 'la materia'}"
                ]
                subtitulo = random.choice(plantillas_subtitulos)
            
            return {
                'titulo': gb_info.get('title', 'Título Desconocido'),
                'subtitulo': subtitulo,
                'isbn': isbn,
                'fecha_publicacion': fecha_publicacion,
                'edicion': gb_info.get('edition', '1ª Edición'),
                'editorial': gb_info.get('publisher', 'Editorial Desconocida'),
                'precio': precio,
                'stock': stock,
                'descripcion': descripcion,
                'num_paginas': gb_info.get('pageCount', random.randint(100, 500)),
                'idioma': gb_info.get('language', 'es'),
                'calificacion': round(calificacion, 2),
                'imagen_portada': imagen_portada,
                'formato': formato,
                'autores': info_autores,
                'categorias': categorias
            }
            
        except Exception as e:
            logging.error(f"Error al procesar libro: {e}")
            return None

    def conectar(self):
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

    def insertar_libros(self, libros: List[Dict[str, Any]]):
        if not self.conn:
            logging.error("No hay conexión a la base de datos")
            return

        cursor = self.conn.cursor()
        
        # Insertar libros
        sql_libros = ("INSERT IGNORE INTO libros "
                    "(titulo, subtitulo, isbn, fecha_publicacion, edicion, editorial, "
                    "precio, stock, descripcion, num_paginas, idioma, "
                    "calificacion, imagen_portada, formato) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        # Insertar autores
        sql_autores = ("INSERT IGNORE INTO autores "
                      "(nombre, apellido, fecha_nacimiento, fecha_fallecimiento, nacionalidad, sitio_web) "
                      "VALUES (%s, %s, %s, %s, %s, %s)")
        
        # Insertar categorías
        sql_categorias = ("INSERT IGNORE INTO categorias "
                         "(nombre, categoria_padre_id) "
                         "VALUES (%s, %s)")
        
        # Insertar relaciones libro-autor
        sql_libro_autor = ("INSERT IGNORE INTO libro_autor "
                          "(libro_id, autor_id) "
                          "VALUES (%s, %s)")
        
        # Insertar relaciones libro-categoría
        sql_libro_categoria = ("INSERT IGNORE INTO libro_categoria "
                           "(libro_id, categoria_id) "
                           "VALUES (%s, %s)")

        try:
            # Insertar libros
            datos_libros = []
            for b in libros:
                datos_libros.append((
                    b.get("titulo", ""),
                    b.get("subtitulo", ""),
                    b.get("isbn", ""),
                    b.get("fecha_publicacion"),
                    b.get("edicion", ""),
                    b.get("editorial", ""),
                    float(b.get("precio", 0)),
                    int(b.get("stock", 0)),
                    b.get("descripcion", ""),
                    int(b.get("num_paginas", 0)) if b.get("num_paginas") else None,
                    b.get("idioma", "es"),
                    float(b.get("calificacion", 3.0)),
                    b.get("imagen_portada", ""),
                    b.get("formato", "Tapa blanda")
                ))
            
            cursor.executemany(sql_libros, datos_libros)
            logging.info(f"Libros insertados/ignorados: {cursor.rowcount}")
            
            # Obtener IDs de libros insertados
            cursor.execute("SELECT libro_id, isbn FROM libros WHERE isbn IN (%s)" % 
                         ','.join(['%s'] * len(libros)), 
                         [b['isbn'] for b in libros])
            ids_libros = {row[1]: row[0] for row in cursor.fetchall()}
            
            # Insertar autores y crear relaciones
            for libro in libros:
                libro_id = ids_libros.get(libro['isbn'])
                if not libro_id:
                    continue
                    
                for autor in libro.get('autores', []):
                    # Insertar autor
                    cursor.execute(sql_autores, (
                        autor.get('nombre', ""),
                        autor.get('apellido', ""),
                        None,  # fecha_nacimiento
                        None,  # fecha_fallecimiento
                        None,  # nacionalidad
                        None   # sitio_web
                    ))
                    autor_id = cursor.lastrowid
                    
                    if autor_id:
                        cursor.execute(sql_libro_autor, (libro_id, autor_id))
            
            # Insertar categorías y crear relaciones
            for libro in libros:
                libro_id = ids_libros.get(libro['isbn'])
                if not libro_id:
                    continue
                    
                for categoria in libro.get('categorias', []):
                    # Insertar categoría principal
                    cursor.execute(sql_categorias, (categoria, None))
                    categoria_id = cursor.lastrowid
                    
                    if categoria_id:
                        cursor.execute(sql_libro_categoria, (libro_id, categoria_id))
            
            self.conn.commit()
            logging.info("Datos insertados correctamente")
            
        except mysql.connector.Error as err:
            logging.error(f"Error al insertar datos: {err}")
            self.conn.rollback()
            sys.exit(1)

    def cerrar(self):
        if self.conn:
            self.conn.close()
            logging.info("Conexión a MySQL cerrada")

def main():
    parser = argparse.ArgumentParser(description='Importar libros a la base de datos desde APIs')
    parser.add_argument("--host", default="localhost", help="Host de la base de datos")
    parser.add_argument("--port", type=int, default=3306, help="Puerto de MySQL")
    parser.add_argument("--user", required=True, help="Usuario de la base de datos")
    parser.add_argument("--password", required=True, help="Contraseña de la base de datos")
    parser.add_argument("--database", default="libreria", help="Nombre de la base de datos")
    args = parser.parse_args()

    importador = ImportadorLibros(args.host, args.user, args.password, args.database, args.port)
    
    logging.info("Iniciando importación de libros...")
    libros = importador.obtener_libros()
    
    importador.conectar()
    importador.insertar_libros(libros)
    importador.cerrar()
    
    logging.info("¡Importación completada!")

if __name__ == "__main__":
    main()