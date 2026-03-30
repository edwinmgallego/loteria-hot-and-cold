import os
import time
import requests
import mysql.connector
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'database': os.getenv('DB_NAME', 'loterias_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

def extraer_premios_secos():
    conexion = None
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if not conexion.is_connected():
            print("❌ No se pudo conectar a MySQL.")
            return

        cursor = conexion.cursor(dictionary=True) # Para traer los resultados como diccionarios
        
        # 1. Obtener la lista de sorteos que ya existen en nuestra tabla principal
        print("🔍 Buscando sorteos disponibles en la base de datos...")
        cursor.execute("SELECT numero_sorteo FROM sorteos_loteria_valle ORDER BY numero_sorteo DESC")
        sorteos_db = cursor.fetchall()
        
        if not sorteos_db:
            print("⚠️ No hay sorteos en la tabla principal. Corre el scraper del premio mayor primero.")
            return

        api_url = 'https://loteriadelvalle.com/resultado_v2/controladores/revisar_controlador.php'
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        total_secos_insertados = 0

        # 2. Iterar por cada sorteo y pedir sus premios secos a la API
        print(f"🚀 Iniciando extracción de premios secos para {len(sorteos_db)} sorteos históricos...")
        
        for fila in sorteos_db:
            sorteo_actual = fila['numero_sorteo']
            
            payload = {
                'datos': 'complemento_secos',
                'sorteo': sorteo_actual
            }
            
            try:
                # Petición a la API
                respuesta = requests.post(api_url, data=payload, headers=headers)
                respuesta.raise_for_status()
                
                # En algunos casos, si no hay secos, la API podría devolver vacío o texto roto
                if not respuesta.text.strip():
                    continue
                    
                datos_secos = respuesta.json()
                lista_insertar = []
                
                # Armar la lista de tuplas para este sorteo
                for seco in datos_secos:
                    tipo = seco.get('seco', 'N/A')
                    numero = seco.get('resultado', '')
                    serie = seco.get('serie', '')
                    
                    if numero and serie:
                        lista_insertar.append((sorteo_actual, tipo, numero, serie))
                
                # 3. Guardar masivamente en la base de datos
                if lista_insertar:
                    query_insert = """
                        INSERT IGNORE INTO premios_secos_valle 
                        (numero_sorteo, tipo_seco, numero_ganador, serie_ganadora)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.executemany(query_insert, lista_insertar)
                    conexion.commit()
                    
                    total_secos_insertados += cursor.rowcount
                    print(f"✅ Sorteo {sorteo_actual}: {cursor.rowcount} premios secos nuevos guardados.")
                
                # Pequeña pausa de 0.2 segundos para no saturar el servidor de la lotería
                time.sleep(0.2)
                
            except requests.exceptions.JSONDecodeError:
                print(f"⚠️ Sorteo {sorteo_actual}: La API no devolvió un JSON válido.")
            except Exception as e:
                print(f"❌ Error en el sorteo {sorteo_actual}: {e}")

        print("=========================================")
        print(f"🎉 ¡PROCESO TERMINADO! Se añadieron un total de {total_secos_insertados} premios secos a tu base de datos.")
        print("=========================================")

    except Exception as e:
        print(f"❌ Error crítico de base de datos: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == '__main__':
    extraer_premios_secos()