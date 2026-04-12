from services.scraper_service import ScraperService
from services.analizador_service import AnalizadorService
from models.loteria_model import LoteriaModel
from views.console_view import ConsoleView
from views.chart_view import ChartView

class MainController:
    def __init__(self, db_conexion):
        self.scraper = ScraperService()
        self.analizador = AnalizadorService()
        self.modelo = LoteriaModel(db_conexion)
        self.vista_consola = ConsoleView()
        self.vista_grafica = ChartView()

    def actualizar_base_datos(self):
        self.vista_consola.mostrar_mensaje("\n⏳ Sincronizando con la Lotería del Valle...")
        datos_api = self.scraper.obtener_sorteos_recientes()
        ultimo = self.modelo.obtener_ultimo_sorteo_guardado()
        
        nuevos = []
        for item in datos_api:
            if int(item['sorteo']) > ultimo:
                nuevos.append((item['sorteo'], item['fecha'].split(' ')[0], item['mayor']['resultado'], item['mayor']['serie'], None))
        
        insertados = self.modelo.guardar_sorteos_nuevos(nuevos)
        self.vista_consola.mostrar_resumen_scraping(len(datos_api), insertados)

    # controllers/main_controller.py

    def generar_recomendaciones(self):
        self.vista_consola.mostrar_mensaje("\n🤖 Analizando patrones históricos...")
        df_n, df_s = self.modelo.obtener_datos_para_analisis()
        grupos = self.analizador.generar_frecuencias(df_n, df_s)
        
        self.vista_consola.mostrar_grupos_frecuencia(grupos)
        
        # 1. Generar los números
        recomendadas = self.analizador.crear_jugadas_hibridas(grupos)
        
        # 2. Guardarlos en la base de datos
        self.modelo.guardar_recomendaciones(recomendadas)
        
        # 3. Mostrarlos en la vista
        self.vista_consola.mostrar_mensaje("✅ Recomendaciones guardadas en el histórico de la BD.")
        self.vista_consola.mostrar_jugadas_hibridas(recomendadas)
        
    def mostrar_graficas_calor(self):
        self.vista_consola.mostrar_mensaje("\n📊 Cargando datos en Pandas para visualización...")
        df_n, df_s = self.modelo.obtener_datos_para_analisis()
        self.vista_grafica.mostrar_heatmap(df_n)