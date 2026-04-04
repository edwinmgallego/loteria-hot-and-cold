import re
import requests
from bs4 import BeautifulSoup

def diagnostico_api_antigua():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url_base = 'https://loteriadelvalle.com/plan-de-premios-antiguos/'
    
    print("🕸️ Iniciando diagnóstico...")
    respuesta = requests.get(url_base, headers=headers)
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    
    # Encontrar solo un enlace para la prueba (ej. 2016)
    enlace_prueba = soup.find('a', href=re.compile(r'resultados-2016'))
    
    if enlace_prueba:
        url_anio = enlace_prueba['href']
        print(f"\n🔍 Explorando la estructura de: {url_anio}")
        
        res_anio = requests.get(url_anio, headers=headers)
        match_url = re.search(r'"data_request_url":"([^"]+)"', res_anio.text)
        
        if match_url:
            ajax_url = match_url.group(1).replace('\\/', '/')
            res_ajax = requests.get(ajax_url, headers=headers)
            
            try:
                datos_anio = res_ajax.json()
                print(f"📦 ¡JSON Descargado! Tipo de dato raíz: {type(datos_anio)}")
                
                # Mostrar las primeras 3 filas para entender la estructura
                print("\n🚨 MOSTRANDO LAS 3 PRIMERAS FILAS EN CRUDO:\n")
                for i, fila in enumerate(datos_anio[:3]):
                    print(f"--- FILA {i+1} ---")
                    print(f"Tipo: {type(fila)}")
                    print(f"Contenido: {fila}\n")
                    
            except Exception as e:
                print(f"❌ Error al decodificar JSON: {e}")
        else:
            print("⚠️ No se encontró la API.")

if __name__ == '__main__':
    diagnostico_api_antigua()