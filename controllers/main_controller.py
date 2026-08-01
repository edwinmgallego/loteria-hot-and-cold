# Al inicio de controllers/main_controller.py añade:
from services.prediccion_service import PrediccionService
from services.scraper_service import ScraperService
from services.analizador_service import AnalizadorService
from models.loteria_model import LoteriaModel
from views.console_view import ConsoleView
from views.chart_view import ChartView

class MainController:
    # Añade este nuevo método a la clase:
    def ejecutar_ia_predictiva(self):
        self.vista_consola.mostrar_mensaje("\n🧠 Inicializando Red de Bosques Aleatorios (Random Forest)...")
        df = self.modelo.obtener_datos_para_analisis()
        
        self.vista_consola.mostrar_mensaje("⚙️ Procesando Feature Engineering...")
        df_preparado = self.prediccion.preparar_datos(df)
        
        self.vista_consola.mostrar_mensaje("🏋️ Entrenando 4 Modelos de Inteligencia Artificial...")
        metricas = self.prediccion.entrenar_modelos(df_preparado)
        
        print("\n📊 RESULTADOS DEL ENTRENAMIENTO (Accuracy):")
        print("Nota: En sistemas estocásticos puros, la precisión esperada es ~10%.")
        for pos, acc in metricas.items():
            print(f"  - Modelo {pos.upper()}: {acc*100:.2f}% de precisión en el set de pruebas.")
            
        # Predicción Final
        self.vista_consola.mostrar_mensaje("\n🔮 Generando predicción para el día de hoy...")
        numero, confianza = self.prediccion.predecir_proximo_sorteo()
        
        print("==================================================")
        print(f"🤖 LA IA PRECUANTIFICA EL SIGUIENTE NÚMERO MAYOR:")
        print(f"   🎟️ NÚMERO: {numero}")
        print(f"   📈 NIVEL DE CONFIANZA DEL MODELO: {confianza*100:.2f}%")
        print("==================================================\n")
        
    def __init__(self, db_conexion):
        self.scraper = ScraperService()
        self.analizador = AnalizadorService()
        self.modelo = LoteriaModel(db_conexion)
        self.vista_consola = ConsoleView()
        self.vista_grafica = ChartView()
        self.prediccion = PrediccionService()

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
        df = self.modelo.obtener_datos_para_analisis()
        grupos = self.analizador.generar_frecuencias(df)
        
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
        df = self.modelo.obtener_datos_para_analisis()
        self.vista_grafica.mostrar_heatmap(df)