import os
import requests
import mysql.connector
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'database': os.getenv('DB_NAME', 'loterias_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

def extraer_desde_api():
    conexion = None
    carpeta_pdfs = 'pdfs_loteria'
    
    if not os.path.exists(carpeta_pdfs):
        os.makedirs(carpeta_pdfs)

    try:
        print("🚀 Conectando a la API oculta de la Lotería del Valle...")
        
        # 1. La URL del controlador que descubriste
        api_url = 'https://loteriadelvalle.com/resultado_v2/controladores/revisar_controlador.php'
        
        # 2. Los datos que la página envía por POST
        payload = {'datos': 'tabla_normal'}
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        respuesta = requests.post(api_url, data=payload, headers=headers)
        respuesta.raise_for_status()
        
        # 3. Convertir la respuesta directamente a un diccionario de Python
        datos_json = respuesta.json()
        
        print(f"📦 ¡Se descargaron {len(datos_json)} sorteos históricos en 1 segundo!")
        
        resultados_mayores = []
        
        # Recorrer el JSON (mucho más fácil que leer HTML)
        for item in datos_json:
            try:
                numero_sorteo = int(item['sorteo'])
                
                # La fecha suele venir como "YYYY-MM-DD HH:MM:SS", nos quedamos con la primera parte
                fecha_mysql = item['fecha'].split(' ')[0] 
                
                # Extraemos el número y la serie navegando por el JSON
                numero_mayor = item['mayor']['resultado']
                serie_mayor = item['mayor']['serie']
                ruta_archivo = None
                
                # --- DESCARGA DEL PDF VÍA POST ---
                pdf_url = 'https://www.loteriadelvalle.com/resultado_v2/vistas/pdfexport.php'
                pdf_payload = {'sorteopdf': numero_sorteo}
                
                try:
                    # Hacemos la petición POST para generar el PDF
                    print(f"📥 Obteniendo PDF del sorteo {numero_sorteo}...")
                    respuesta_pdf = requests.post(pdf_url, data=pdf_payload, headers=headers)
                    
                    if respuesta_pdf.status_code == 200:
                        ruta_archivo = os.path.join(carpeta_pdfs, f"sorteo_{numero_sorteo}.pdf")
                        with open(ruta_archivo, 'wb') as archivo:
                            archivo.write(respuesta_pdf.content)
                except Exception as e:
                    print(f"⚠️ Error al guardar PDF {numero_sorteo}: {e}")
                
                # Agregamos la fila a nuestra lista para MySQL
                resultados_mayores.append((numero_sorteo, fecha_mysql, numero_mayor, serie_mayor, ruta_archivo))
                
            except KeyError as e:
                print(f"⚠️ Fila omitida por estructura incompleta: falta {e}")

        # 4. CARGAR EN MYSQL
        conexion = mysql.connector.connect(**DB_CONFIG)
        
        if conexion.is_connected() and resultados_mayores:
            cursor = conexion.cursor()
            
            # Usamos INSERT IGNORE por si lo corres varias veces
            query = """
                INSERT IGNORE INTO sorteos_loteria_valle 
                (numero_sorteo, fecha_sorteo, numero_mayor, serie_mayor, ruta_pdf)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            cursor.executemany(query, resultados_mayores)
            conexion.commit()
            
            print(f'✅ ¡Éxito total! Se insertaron {cursor.rowcount} registros nuevos en MySQL.')
            
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == '__main__':
    extraer_desde_api()