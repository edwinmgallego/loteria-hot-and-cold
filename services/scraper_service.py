import requests

class ScraperService:
    def __init__(self):
        self.api_url = 'https://loteriadelvalle.com/resultado_v2/controladores/revisar_controlador.php'
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def obtener_sorteos_recientes(self):
        payload = {'datos': 'tabla_normal'}
        respuesta = requests.post(self.api_url, data=payload, headers=self.headers)
        respuesta.raise_for_status()
        return respuesta.json()