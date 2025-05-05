import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Conexión establecida con la base de datos")
                return True
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.connection and self.connection.is_connected():
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("Conexión cerrada")
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta SQL"""
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return False
    
    def fetch_all(self, query, params=None):
        """Ejecuta una consulta y devuelve todos los resultados"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"Error al obtener datos: {e}")
            return []
    
    def fetch_one(self, query, params=None):
        """Ejecuta una consulta y devuelve un solo resultado"""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        except Error as e:
            print(f"Error al obtener datos: {e}")
            return None
    
    def call_procedure(self, procedure_name, params=None):
        """Llama a un procedimiento almacenado"""
        try:
            self.cursor.callproc(procedure_name, params or ())
            # Obtener resultados si los hay
            results = []
            for result in self.cursor.stored_results():
                results.extend(result.fetchall())
            self.connection.commit()
            return results
        except Error as e:
            print(f"Error al llamar al procedimiento {procedure_name}: {e}")
            return []