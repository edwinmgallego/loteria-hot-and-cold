import os
import re
import requests
from bs4 import BeautifulSoup
import mysql.connector
from dotenv import load_dotenv

# Cargar configuración de la BD
load_dotenv()
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'database': os.getenv('DB_NAME', 'loterias_db'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Diccionario para traducir meses en español a números
MESES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

def parsear_fecha_espanol(fecha_texto):
    """Convierte '28 de diciembre de 2016' a '2016-12-28'"""
    try:
        # Limpiamos por si hay HTML
        texto_limpio = BeautifulSoup(fecha_texto, 'html.parser').text.strip().lower()
        # Buscamos el patrón: 2 digitos, la palabra 'de', letras, 'de', 4 digitos
        match = re.search(r'(\d{1,2})\s+de\s+([a-z]+)\s+de\s+(\d{4})', texto_limpio)
        if match:
            dia = match.group(1).zfill(2)
            mes_texto = match.group(2)
            anio = match.group(3)
            mes = MESES.get(mes_texto, '01') # Si falla el mes, pone enero
            return f"{anio}-{mes}-{dia}"
    except Exception:
        pass
    return '2000-01-01' # Fecha por defecto de rescate

def raspar_historico_antiguo():
    conexion = None
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        url_base = 'https://loteriadelvalle.com/plan-de-premios-antiguos/'
        
        print("🕸️ Iniciando la Araña para buscar años antiguos...")
        respuesta = requests.get(url_base, headers=headers)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        enlaces = soup.find_all('a', href=re.compile(r'resultados-20\d{2}'))
        urls_anios = set([a['href'] for a in enlaces])
        
        total_mayores = 0
        total_secos = 0
        
        for url_anio in urls_anios:
            print(f"\n🔍 Explorando: {url_anio}")
            res_anio = requests.get(url_anio, headers=headers)
            html_anio = res_anio.text
            
            match_url = re.search(r'"data_request_url":"([^"]+)"', html_anio)
            if not match_url:
                print("⚠️ No se encontró la API de Ninja Tables.")
                continue
                
            ajax_url = match_url.group(1).replace('\\/', '/')
            print(f"🎯 ¡API secreta encontrada! Descargando datos...")
            
            res_ajax = requests.get(ajax_url, headers=headers)
            datos_anio = res_ajax.json()
            print(f"📦 Se descargaron {len(datos_anio)} registros brutos.")
            
            mayores_a_insertar = []
            secos_a_insertar = []
            errores_locales = 0
            
            # 5. Extraer directamente de la llave 'value'
            for fila in datos_anio:
                try:
                    # Entramos a la llave donde realmente están los datos
                    if not isinstance(fila, dict) or 'value' not in fila:
                        errores_locales += 1
                        continue
                        
                    datos = fila['value']
                    
                    sorteo_raw = str(datos.get('sorteo', ''))
                    numero_raw = str(datos.get('numero', ''))
                    serie_raw = str(datos.get('series', ''))
                    premio_raw = str(datos.get('premio', ''))
                    fecha_raw = str(datos.get('fecha', ''))
                    
                    # Limpiamos HTML
                    sorteo_cl = BeautifulSoup(sorteo_raw, 'html.parser').text.strip()
                    numero_cl = BeautifulSoup(numero_raw, 'html.parser').text.strip()
                    serie_cl = BeautifulSoup(serie_raw, 'html.parser').text.strip()
                    premio_cl = BeautifulSoup(premio_raw, 'html.parser').text.strip().upper()
                    
                    # Extraemos solo los dígitos
                    match_sorteo = re.search(r'\d+', sorteo_cl)
                    match_numero = re.search(r'\d+', numero_cl)
                    match_serie = re.search(r'\d+', serie_cl)
                    
                    if not match_sorteo or not match_numero or not match_serie:
                        errores_locales += 1
                        continue
                        
                    sorteo = int(match_sorteo.group())
                    numero = match_numero.group().zfill(4)
                    serie = match_serie.group().zfill(3)
                    
                    # Traducir fecha
                    fecha_mysql = parsear_fecha_espanol(fecha_raw)
                    
                    # Clasificar
                    if 'MAYOR' in premio_cl:
                        mayores_a_insertar.append((sorteo, fecha_mysql, numero, serie, None))
                    else:
                        secos_a_insertar.append((sorteo, premio_cl, numero, serie))
                        
                except Exception as e:
                    errores_locales += 1
            
            if errores_locales > 0:
                print(f"⚠️ Se descartaron {errores_locales} filas inválidas.")
            
            # 6. Guardar en la Base de Datos
            insertados_secos = 0
            if mayores_a_insertar:
                query_mayor = """
                    INSERT IGNORE INTO sorteos_loteria_valle 
                    (numero_sorteo, fecha_sorteo, numero_mayor, serie_mayor, ruta_pdf)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.executemany(query_mayor, mayores_a_insertar)
                conexion.commit()
                total_mayores += len(mayores_a_insertar)
                
            if secos_a_insertar:
                query_seco = """
                    INSERT IGNORE INTO premios_secos_valle 
                    (numero_sorteo, tipo_seco, numero_ganador, serie_ganadora)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.executemany(query_seco, secos_a_insertar)
                conexion.commit()
                insertados_secos = len(secos_a_insertar)
                total_secos += insertados_secos
                
            print(f"✅ Procesados e insertados: {len(mayores_a_insertar)} Mayores y {insertados_secos} Secos.")

        print("\n==================================================")
        print(f"🎉 ¡EXTRACCIÓN HISTÓRICA ANTIGUA COMPLETADA!")
        print(f"   Se añadieron {total_mayores} Premios Mayores.")
        print(f"   Se añadieron {total_secos} Premios Secos.")
        print("==================================================")

    except Exception as e:
        print(f"❌ Error crítico en el proceso: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == '__main__':
    raspar_historico_antiguo()