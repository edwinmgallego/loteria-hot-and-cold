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

    def guardar_sorteos_nuevos(self, lista_sorteos):
        if not lista_sorteos:
            return 0
        cursor = self.conexion.cursor()
        query = """
            INSERT IGNORE INTO sorteos_loteria_valle 
            (numero_sorteo, fecha_sorteo, numero_mayor, serie_mayor, ruta_pdf)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(query, lista_sorteos)
        self.conexion.commit()
        filas_insertadas = cursor.rowcount
        cursor.close()
        return filas_insertadas

    def obtener_datos_para_analisis(self):
        """Usa SQLAlchemy para cargar los datos directo a Pandas"""
        cadena_conexion = f"mysql+pymysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', '127.0.0.1')}/{os.getenv('DB_NAME', 'loterias_db')}"
        motor = create_engine(cadena_conexion)

        query_n = "SELECT numero_mayor AS numero FROM sorteos_loteria_valle UNION ALL SELECT numero_ganador AS numero FROM premios_secos_valle"
        query_s = "SELECT serie_mayor AS serie FROM sorteos_loteria_valle UNION ALL SELECT serie_ganadora AS serie FROM premios_secos_valle"
        
        df_n = pd.read_sql(query_n, motor)
        df_s = pd.read_sql(query_s, motor)
        
        df_n['numero'] = df_n['numero'].astype(str).str.zfill(4)
        df_s['serie'] = df_s['serie'].astype(str).str.zfill(3)
        
        return df_n, df_s
    # models/loteria_model.py

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