import os
import pandas as pd
from sqlalchemy import create_engine

class LoteriaModel:
    def __init__(self, conexion):
        self.conexion = conexion

    def obtener_ultimo_sorteo_guardado(self):
        cursor = self.conexion.cursor()
        cursor.execute("SELECT MAX(numero_sorteo) FROM sorteos_loteria_valle")
        resultado = cursor.fetchone()
        cursor.close()
        return resultado[0] if resultado[0] else 0
    def obtener_historico_recomendaciones(self, limite=30):
        """Usa SQLAlchemy para traer el historial sin generar advertencias de Pandas."""
        cadena_conexion = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', '127.0.0.1')}/{os.getenv('DB_NAME', 'loterias_db')}"
        motor = create_engine(cadena_conexion)
        
        query = f"SELECT numero, serie, fecha_hora FROM recomendaciones_loteria ORDER BY fecha_hora DESC LIMIT {limite}"
        
        return pd.read_sql(query, motor)
        
    def guardar_sorteos_nuevos(self, lista_sorteos, lista_balotas):
        """Guarda los datos crudos en la tabla principal y los atómicos en la secundaria"""
        if not lista_sorteos:
            return 0
            
        cursor = self.conexion.cursor()
        
        try:
            # 1. Guardar en la tabla principal (Datos Crudos)
            query_principal = """
                INSERT IGNORE INTO sorteos_loteria_valle 
                (numero_sorteo, fecha_sorteo, numero_mayor, serie_mayor, ruta_pdf)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.executemany(query_principal, lista_sorteos)
            
            # 2. Guardar en la tabla secundaria (Datos Atómicos para la IA)
            query_balotas = """
                INSERT IGNORE INTO balotas_loteria_valle 
                (numero_sorteo, balota_1, balota_2, balota_3, balota_4, serie_1, serie_2, serie_3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(query_balotas, lista_balotas)
            
            self.conexion.commit()
            filas_insertadas = cursor.rowcount
            
        except Exception as e:
            self.conexion.rollback() # Si hay un error, deshace todo para no dejar datos a medias
            print(f"Error guardando en BD: {e}")
            filas_insertadas = 0
            
        finally:
            cursor.close()
            
        return filas_insertadas

    def guardar_log_backtesting(self, resultados):
        """
        Recibe la lista de diccionarios del backtesting y los guarda.
        """
        if not resultados:
            return
        
        cursor = self.conexion.cursor()
        query = """
            INSERT INTO log_backtesting (fecha_sorteo, prediccion_ia, resultado_real, aciertos)
            VALUES (%s, %s, %s, %s)
        """
        
        # Preparamos los datos desde la lista de diccionarios que devuelve el servicio
        datos_batch = [
            (r['fecha'], r['ia'], r['real'], r['aciertos']) 
            for r in resultados
        ]
        
        # Estas eran las líneas que faltaban aquí:
        cursor.executemany(query, datos_batch)
        self.conexion.commit()
        cursor.close()

    def obtener_datos_para_analisis(self):
        """Une las dos tablas para entregar datos listos para estadística e IA"""
        cadena_conexion = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', '127.0.0.1')}/{os.getenv('DB_NAME', 'loterias_db')}"
        motor = create_engine(cadena_conexion)

        # Hacemos un JOIN para tener la fecha y las balotas en un solo lugar
        query = """
            SELECT 
                s.fecha_sorteo, 
                b.balota_1, b.balota_2, b.balota_3, b.balota_4,
                b.serie_1, b.serie_2, b.serie_3
            FROM sorteos_loteria_valle s
            JOIN balotas_loteria_valle b ON s.numero_sorteo = b.numero_sorteo
            ORDER BY s.fecha_sorteo ASC
        """
        
        df = pd.read_sql(query, motor)
        return df
    
    def guardar_recomendaciones(self, lista_recomendaciones):
        """
        Guarda los números y series recomendados en la base de datos.
        lista_recomendaciones: lista de tuplas [('numero', 'serie'), ...]
        """
        if not lista_recomendaciones:
            return 0
            
        cursor = self.conexion.cursor()
        query = "INSERT INTO recomendaciones_loteria (numero, serie) VALUES (%s, %s)"
        
        # MySQL se encarga de la fecha y hora automáticamente con DEFAULT CURRENT_TIMESTAMP
        cursor.executemany(query, lista_recomendaciones)
        self.conexion.commit()
        filas = cursor.rowcount
        cursor.close()
        return filas
    def obtener_historial_ia(self):
        """
        Obtiene los resultados de los backtestings pasados para mostrarlos en la pestaña "Mi Histórico".
        """
        cursor = self.conexion.cursor()
        query = """
            SELECT fecha_sorteo, prediccion_ia, resultado_real, aciertos 
            FROM log_backtesting 
            ORDER BY fecha_sorteo DESC 
            LIMIT 50
        """
        cursor.execute(query)
        filas = cursor.fetchall()
        columnas = [i[0] for i in cursor.description]
        cursor.close()
        
        # Convertir a DataFrame de Pandas para facilitar el manejo
        df = pd.DataFrame(filas, columns=columnas)
        return df